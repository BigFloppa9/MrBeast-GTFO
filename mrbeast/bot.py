import asyncio
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from .config import MAX_BAN_DELETE_MINUTES, effective_reason, step_reason, steps_for
from .i18n import t
from .logstore import MAX_IMAGE_BYTES, MAX_IMAGES_PER_LOG, cut, save_image_async
from .state import state
from .utils import apply_patch, fmt_duration, parse_duration

logger = logging.getLogger("mrbeast.bot")

DISCORD_MAX_TIMEOUT = timedelta(days=28)
MEDIA_DOMAINS = ("discordapp.com", "discordapp.net")
MAX_DOWNLOADS = 12
RETENTION_SCAN_DAYS = 90
SCAN_LIMIT = 3000
BULK_DELETE_AGE = timedelta(days=13)


def lang() -> str:
    return state.config.bot_lang


def is_admin_somewhere(bot: commands.Bot, user_id: int) -> bool:
    for guild in bot.guilds:
        if guild.owner_id == user_id:
            return True
        member = guild.get_member(user_id)
        if member and member.guild_permissions.administrator:
            return True
    return False


def trusted_media(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return any(host == d or host.endswith("." + d) for d in MEDIA_DOMAINS)


def image_urls(message: discord.Message) -> list[str]:
    urls = []
    for a in message.attachments:
        if a.content_type and a.content_type.startswith("image/") and a.size <= MAX_IMAGE_BYTES:
            urls.append(a.url)
    for e in message.embeds:
        for media in (e.image, e.thumbnail):
            if media and media.proxy_url and trusted_media(media.proxy_url):
                urls.append(media.proxy_url)
    return urls


async def fetch_bytes(session: aiohttp.ClientSession, url: str) -> bytes | None:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15), proxy=state.proxy_url) as resp:
            if resp.status != 200:
                return None
            buf = bytearray()
            async for chunk in resp.content.iter_chunked(65536):
                buf.extend(chunk)
                if len(buf) > MAX_IMAGE_BYTES:
                    return None
            return bytes(buf)
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return None


async def capture_images(messages: list[discord.Message]) -> list[dict]:
    try:
        urls = []
        for m in messages:
            urls.extend(image_urls(m))
        counts: dict[str, int] = {}
        async with aiohttp.ClientSession() as session:
            for url in urls[:MAX_DOWNLOADS]:
                data = await fetch_bytes(session, url)
                if not data:
                    continue
                name = await save_image_async(data)
                if not name:
                    continue
                if name not in counts:
                    if len(counts) >= MAX_IMAGES_PER_LOG:
                        continue
                    counts[name] = 0
                counts[name] += 1
        return [{"file": n, "count": c} for n, c in counts.items()]
    except Exception as e:
        logger.error(f"Image capture error: {e}")
        return []


async def send_log(guild: discord.Guild, embed: discord.Embed) -> discord.Message | None:
    ch_id = state.settings.get(guild.id).get("log_channel", 0)
    if not ch_id:
        return None
    ch = guild.get_channel(ch_id)
    if not ch:
        return None
    perms = ch.permissions_for(guild.me)
    if not (perms.send_messages and perms.embed_links):
        logger.warning(f"Missing perms in log channel #{ch.name}")
        return None
    try:
        return await ch.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException) as e:
        logger.error(f"Log send error: {e}")
        return None


def embed_mentions(message: discord.Message, ids: set[str]) -> bool:
    for embed in message.embeds:
        texts = [embed.title or "", embed.description or "", embed.footer.text if embed.footer else ""]
        texts += [f.value or "" for f in embed.fields]
        blob = "\n".join(texts)
        if any(i in blob for i in ids):
            return True
    return False


async def scrub_discord_logs(bot: commands.Bot, ids: set[str], refs: list[dict]) -> dict:
    result = {"deleted": 0, "scanned": 0, "skipped": False}
    if not ids and not refs:
        return result
    if not bot or not bot.is_ready() or not bot.user:
        result["skipped"] = True
        return result
    gone: set[int] = set()
    for ref in refs:
        try:
            channel = bot.get_channel(int(ref["channel"])) or await bot.fetch_channel(int(ref["channel"]))
            message = await channel.fetch_message(int(ref["message"]))
        except (KeyError, ValueError, TypeError, discord.HTTPException):
            continue
        if message.author.id == bot.user.id:
            try:
                await message.delete()
                gone.add(message.id)
                result["deleted"] += 1
            except discord.HTTPException:
                pass
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_SCAN_DAYS)
    for guild in bot.guilds:
        channel_id = state.settings.get(guild.id).get("log_channel", 0)
        channel = guild.get_channel(channel_id) if channel_id else None
        if not isinstance(channel, discord.TextChannel) or not ids:
            continue
        if not channel.permissions_for(guild.me).read_message_history:
            continue
        try:
            async for message in channel.history(limit=SCAN_LIMIT, after=cutoff):
                result["scanned"] += 1
                if message.id in gone or message.author.id != bot.user.id:
                    continue
                if embed_mentions(message, ids):
                    try:
                        await message.delete()
                        result["deleted"] += 1
                    except discord.HTTPException:
                        pass
                    await asyncio.sleep(0.4)
        except discord.HTTPException as e:
            logger.error(f"Log channel scan error in {guild.id}: {e}")
    return result


async def apply_timeout(guild: discord.Guild, target: discord.Member, s: dict) -> Exception | None:
    timeout_td = min(timedelta(minutes=s["timeout_duration"]), DISCORD_MAX_TIMEOUT)
    try:
        await target.timeout(datetime.now(timezone.utc) + timeout_td, reason=effective_reason(s, lang())[:512])
        return None
    except Exception as e:
        return e


async def apply_step(guild: discord.Guild, target: discord.Member, step: dict, reason: str) -> Exception | None:
    try:
        if step["action"] == "ban":
            seconds = min(step["delete"], MAX_BAN_DELETE_MINUTES) * 60
            await guild.ban(target, reason=reason[:512], delete_message_seconds=seconds)
        else:
            timeout_td = min(timedelta(minutes=step["duration"]), DISCORD_MAX_TIMEOUT)
            await target.timeout(datetime.now(timezone.utc) + timeout_td, reason=reason[:512])
        return None
    except Exception as e:
        return e


async def send_reason(guild: discord.Guild, target: discord.Member, reason: str):
    if not state.settings.get(guild.id).get("dm_reason", True):
        return
    try:
        await target.send(t(lang(), "dm_reason_title", server=guild.name, reason=reason)[:2000])
    except (discord.Forbidden, discord.HTTPException):
        pass


async def delete_messages(ch, msgs: list[discord.Message]):
    bulk_after = datetime.now(timezone.utc) - BULK_DELETE_AGE
    recent = [m for m in msgs if m.created_at > bulk_after]
    old = [m for m in msgs if m.created_at <= bulk_after]
    for i in range(0, len(recent), 100):
        chunk = recent[i:i + 100]
        if len(chunk) == 1:
            await chunk[0].delete()
        else:
            await ch.delete_messages(chunk)
    for m in old:
        await m.delete()
        await asyncio.sleep(0.5)


async def purge_messages(guild: discord.Guild, target: discord.Member, s: dict, source: str) -> int:
    deleted = 0
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=s["delete_window"])
    all_channels = list(guild.text_channels) + list(guild.voice_channels)

    for ch in all_channels:
        perms = ch.permissions_for(guild.me)
        if not (perms.read_message_history and perms.manage_messages):
            continue
        try:
            msgs = [m async for m in ch.history(limit=500, after=cutoff) if m.author.id == target.id]
            if msgs:
                await delete_messages(ch, msgs)
                deleted += len(msgs)
                logger.info(f"[{source}] Deleted {len(msgs)} in #{ch.name}")
        except discord.HTTPException as e:
            logger.error(f"[{source}] Error in #{ch.name}: {e}")
        await asyncio.sleep(0.5)

    logger.info(f"[{source}] Total deleted: {deleted} for {target}")
    return deleted


def build_embed(source: str, target: discord.Member, s: dict, deleted: int | None,
                trigger_msg: discord.Message | None = None, moderator: discord.abc.User | None = None,
                step: dict | None = None, strike: tuple[int, int] | None = None) -> discord.Embed:
    lg = lang()
    auto = source == "auto"
    embed = discord.Embed(
        title=t(lg, "title_auto" if auto else "title_manual"),
        color=discord.Color.red() if auto else discord.Color.orange(),
        timestamp=datetime.now(timezone.utc),
    )
    embed.add_field(name=t(lg, "offender"), value=f"{target.mention} (`{target.id}`)", inline=False)
    if auto and trigger_msg is not None:
        content = (trigger_msg.content or t(lg, "image_placeholder"))[:900]
        embed.add_field(name=t(lg, "trigger"), value=f"[Jump]({trigger_msg.jump_url})\n{content}", inline=False)
    if moderator is not None:
        embed.add_field(name=t(lg, "moderator"), value=moderator.mention, inline=False)
    step = step or {"action": "timeout", "duration": s["timeout_duration"], "delete": s["delete_window"]}
    window = fmt_duration(step["delete"])
    if step["action"] == "ban":
        first_line = t(lg, "ban_line")
        deleted_line = t(lg, "deleted_ban", window=window)
    else:
        first_line = t(lg, "timeout_line", duration=fmt_duration(step["duration"]))
        deleted_line = t(lg, "deleted_auto", count=deleted, window=window) if auto else t(lg, "deleted_manual", count=deleted)
    lines = [first_line, deleted_line]
    if strike and strike[1] > 1:
        lines.insert(0, t(lg, "strike_line", n=strike[0], total=strike[1]))
    embed.add_field(name=t(lg, "action"), value="\n".join(lines), inline=False)
    if auto and trigger_msg is not None:
        embed.set_footer(text=f"#{trigger_msg.channel.name}")
    return embed


def person(user) -> dict:
    return {"display": cut(user.display_name), "username": cut(user.name), "id": str(user.id)}


def record_log(source: str, guild: discord.Guild, target: discord.Member, s: dict, deleted: int | None,
               trigger_msg: discord.Message | None = None, images: list[dict] | None = None,
               moderator: discord.abc.User | None = None, step: dict | None = None,
               strike: tuple[int, int] | None = None, message: discord.Message | None = None):
    trigger = None
    if trigger_msg is not None:
        trigger = {
            "text": cut(trigger_msg.content),
            "channel": cut(trigger_msg.channel.name),
            "url": f"https://discord.com/channels/{guild.id}/{trigger_msg.channel.id}",
            "images": images or [],
        }
    state.logs.add({
        "kind": source,
        "guild": {"id": str(guild.id), "name": cut(guild.name)},
        "offender": person(target),
        "moderator": person(moderator) if moderator is not None else None,
        "trigger": trigger,
        "timeout": (step or {}).get("duration", s["timeout_duration"]) if (step or {}).get("action") != "ban" else 0,
        "deleted": deleted,
        "window": (step or {}).get("delete", s["delete_window"]) if source == "auto" else None,
        "action": (step or {}).get("action", "timeout"),
        "strike": {"n": strike[0], "total": strike[1]} if strike else None,
        "discord": {"channel": str(message.channel.id), "message": str(message.id)} if message is not None else None,
    })


async def set_log_channel(guild: discord.Guild, channel: discord.TextChannel) -> list[str]:
    lg = lang()
    perms = channel.permissions_for(guild.me)
    missing = [
        label for label, ok in (
            (t(lg, "perm_view_channel"), perms.view_channel),
            (t(lg, "perm_send_messages"), perms.send_messages),
            (t(lg, "perm_embed_links"), perms.embed_links),
        ) if not ok
    ]
    if missing:
        try:
            await channel.set_permissions(
                guild.me, view_channel=True, send_messages=True, embed_links=True, reason="MrBeastLog self-grant"
            )
        except (discord.Forbidden, discord.HTTPException):
            return missing
    state.settings.get(guild.id)["log_channel"] = channel.id
    state.settings.save()
    return []


class GuardTree(app_commands.CommandTree):
    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        lg = lang()
        if isinstance(error, (app_commands.MissingPermissions, app_commands.CheckFailure)):
            message = t(lg, "err_no_permission")
        else:
            logger.error(f"Command error: {error}")
            message = t(lg, "err_generic")
        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException:
            pass


class Guard(commands.Cog):
    def __init__(self, bot: "GuardBot"):
        self.bot = bot
        self.image_tracker = defaultdict(lambda: defaultdict(list))
        self.busy: set[tuple[int, int]] = set()
        self.cooldown: dict[tuple[int, int], float] = {}
        self.hinted: dict[int, float] = {}

    async def run_auto(self, guild: discord.Guild, target: discord.Member, trigger_msg: discord.Message, evidence: list):
        s = state.settings.get(guild.id)
        steps = steps_for(s)
        done = state.strikes.peek(guild.id, target.id, s["warn_reset_days"])
        index = min(done, len(steps) - 1)
        step = steps[index]
        total = len(steps)
        reason = step_reason(s, index, total, lang())
        if step["action"] == "ban":
            await send_reason(guild, target, reason)
        err = await apply_step(guild, target, step, reason)
        if err is None and step["action"] != "ban":
            await send_reason(guild, target, reason)
        if err is not None:
            if isinstance(err, discord.Forbidden):
                logger.warning(f"[auto] Cannot {step['action']} {target}")
            else:
                logger.error(f"[auto] {step['action']} error: {err}")
            return
        state.strikes.commit(guild.id, target.id, done + 1)
        logger.info(f"[auto] {step['action']} applied to {target} (detection {index + 1}/{total})")
        images = await capture_images(evidence)
        deleted = None
        if step["action"] != "ban":
            window_settings = dict(s, delete_window=step["delete"])
            deleted = await purge_messages(guild, target, window_settings, "auto")
        strike = (index + 1, total)
        message = await send_log(guild, build_embed("auto", target, s, deleted, trigger_msg=trigger_msg, step=step, strike=strike))
        record_log("auto", guild, target, s, deleted, trigger_msg=trigger_msg, images=images, step=step, strike=strike, message=message)

    async def guarded_auto(self, guild: discord.Guild, target: discord.Member, trigger_msg: discord.Message, evidence: list):
        key = (guild.id, target.id)
        try:
            await self.run_auto(guild, target, trigger_msg, evidence)
        except Exception as e:
            logger.error(f"[auto] Unexpected error: {e!r}")
        finally:
            self.busy.discard(key)
            self.cooldown[key] = time.monotonic() + 60

    async def dm_hint(self, message: discord.Message):
        now = time.monotonic()
        if now - self.hinted.get(message.author.id, 0) < 30:
            return
        self.hinted[message.author.id] = now
        logger.info(f"[DM] message from {message.author}")
        try:
            await message.channel.send(t(lang(), "dm_hint"))
        except discord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            await self.dm_hint(message)
            return
        if state.config.bot_state == "paused":
            return

        has_image = (
            any(a.content_type and a.content_type.startswith("image/") for a in message.attachments)
            or any(e.image or e.thumbnail for e in message.embeds)
        )
        if not has_image:
            return

        gid, uid = message.guild.id, message.author.id
        if (gid, uid) in self.busy or self.cooldown.get((gid, uid), 0) > time.monotonic():
            return

        s = state.settings.get(gid)
        now = datetime.now(timezone.utc)
        tracker = self.image_tracker[gid][uid]
        tracker.append({"time": now, "ch": message.channel.id, "msg": message})
        self.image_tracker[gid][uid] = [e for e in tracker if (now - e["time"]).total_seconds() <= s["auto_window_seconds"]]
        tracker = self.image_tracker[gid][uid]

        unique_chs = {e["ch"] for e in tracker}
        logger.info(f"[Tracker] {message.author}: {len(tracker)} images in {len(unique_chs)} channels")

        if len(tracker) >= s["auto_min_images"] and len(unique_chs) >= s["auto_min_channels"]:
            self.busy.add((gid, uid))
            evidence = [e["msg"] for e in tracker]
            self.image_tracker[gid][uid] = []
            logger.info(f"[AutoDetect] Triggered for {message.author}")
            member = message.guild.get_member(uid)
            if member:
                asyncio.create_task(self.guarded_auto(message.guild, member, message, evidence))
            else:
                self.busy.discard((gid, uid))

    @app_commands.command(name="mrbeast", description="Timeout a compromised account and delete their messages")
    @app_commands.describe(target="User to timeout (@mention or ID)")
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.guild_only()
    async def mrbeast(self, interaction: discord.Interaction, target: discord.Member):
        lg = lang()
        await interaction.response.defer(ephemeral=True)
        s = state.settings.get(interaction.guild.id)

        err = await apply_timeout(interaction.guild, target, s)
        if err is not None:
            if isinstance(err, discord.Forbidden):
                await interaction.followup.send(t(lg, "manual_no_permission"), ephemeral=True)
            else:
                await interaction.followup.send(t(lg, "manual_error", error=err), ephemeral=True)
            return

        deleted = await purge_messages(interaction.guild, target, s, "manual")
        message = await send_log(interaction.guild, build_embed("manual", target, s, deleted, moderator=interaction.user))
        record_log("manual", interaction.guild, target, s, deleted, moderator=interaction.user, message=message)

        await interaction.followup.send(
            t(lg, "manual_done", name=target.display_name, duration=fmt_duration(s["timeout_duration"]),
              count=deleted, window=fmt_duration(s["delete_window"])),
            ephemeral=True,
        )

    @app_commands.command(name="mrbeastlog", description="Set the log channel for MrBeast actions")
    @app_commands.describe(channel="Channel to send logs to")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def mrbeastlog(self, interaction: discord.Interaction, channel: discord.TextChannel):
        lg = lang()
        missing = await set_log_channel(interaction.guild, channel)
        if missing:
            await interaction.response.send_message(
                t(lg, "log_missing_perms", channel=channel.mention, missing="` `".join(missing), name=channel.name),
                ephemeral=True,
            )
            return
        await interaction.response.send_message(t(lg, "log_set", channel=channel.mention), ephemeral=True)

    @app_commands.command(name="mrbeastconfig", description="Configure MrBeast bot settings")
    @app_commands.describe(
        reason="Timeout reason shown to users (leave empty to keep current)",
        timeout="Timeout duration, e.g. 1d / 12h / 30m / 1d12h (max 28d)",
        deletetime="How far back to delete messages, e.g. 24h / 7d / 30m",
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def mrbeastconfig(self, interaction: discord.Interaction, reason: str = None, timeout: str = None, deletetime: str = None):
        lg = lang()
        s = state.settings.get(interaction.guild.id)
        changes = []
        errors = []

        if reason is not None:
            s["timeout_reason"] = reason
            changes.append(t(lg, "cfg_reason_updated"))

        if timeout is not None:
            td = parse_duration(timeout)
            if td is None:
                errors.append(t(lg, "cfg_timeout_invalid", value=timeout))
            elif td > DISCORD_MAX_TIMEOUT:
                errors.append(t(lg, "cfg_timeout_long"))
            elif td.total_seconds() < 60:
                errors.append(t(lg, "cfg_timeout_short"))
            else:
                s["timeout_duration"] = int(td.total_seconds() // 60)
                changes.append(t(lg, "cfg_timeout_set", duration=fmt_duration(s["timeout_duration"])))

        if deletetime is not None:
            td = parse_duration(deletetime)
            if td is None:
                errors.append(t(lg, "cfg_delete_invalid", value=deletetime))
            elif td.total_seconds() < 60:
                errors.append(t(lg, "cfg_delete_short"))
            else:
                s["delete_window"] = int(td.total_seconds() // 60)
                changes.append(t(lg, "cfg_delete_set", duration=fmt_duration(s["delete_window"])))

        if errors:
            await interaction.response.send_message("\n".join(errors), ephemeral=True)
            return

        if not changes:
            shown = effective_reason(s, lg)
            await interaction.response.send_message(
                t(lg, "cfg_current", timeout=fmt_duration(s["timeout_duration"]), window=fmt_duration(s["delete_window"]),
                  reason=f"{shown[:100]}{'...' if len(shown) > 100 else ''}"),
                ephemeral=True,
            )
            return

        state.settings.save()
        await interaction.response.send_message("\n".join(changes), ephemeral=True)

    @app_commands.command(name="reg", description="Link your account as the web panel moderator (DM only)")
    @app_commands.describe(code="Code shown in the web panel")
    @app_commands.allowed_contexts(guilds=False, dms=True, private_channels=False)
    async def reg(self, interaction: discord.Interaction, code: str):
        lg = lang()
        logger.info(f"[DM] /reg from {interaction.user}")
        if not is_admin_somewhere(self.bot, interaction.user.id):
            await interaction.response.send_message(t(lg, "dm_reg_not_admin"))
            return
        if not state.reg_code.consume(code):
            await interaction.response.send_message(t(lg, "dm_reg_bad"))
            return
        label = f"{interaction.user.display_name} ({interaction.user.name})"
        if not state.config.add_moderator(interaction.user.id, cut(label, 100)):
            await interaction.response.send_message(t(lg, "dm_reg_full"))
            return
        await interaction.response.send_message(t(lg, "dm_reg_ok"))

    @app_commands.command(name="log", description="Get a password reset code for the web panel (DM only)")
    @app_commands.allowed_contexts(guilds=False, dms=True, private_channels=False)
    async def log(self, interaction: discord.Interaction):
        lg = lang()
        logger.info(f"[DM] /log from {interaction.user}")
        if not state.config.is_moderator(interaction.user.id):
            await interaction.response.send_message(t(lg, "dm_log_denied"))
            return
        code = state.reset.issue_code()
        if code is None:
            await interaction.response.send_message(t(lg, "dm_log_closed"))
            return
        await interaction.response.send_message(t(lg, "dm_log_code", code=code))


class GuardBot(commands.Bot):
    def __init__(self, proxy: str | None = None):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            help_command=None,
            tree_cls=GuardTree,
            proxy=proxy,
        )
        self.ready_at: float | None = None

    async def setup_hook(self):
        await self.add_cog(Guard(self))
        try:
            await self.tree.sync()
        except discord.HTTPException as e:
            logger.error(f"Command sync error: {e}")

    async def on_ready(self):
        self.ready_at = time.time()
        logger.info(f"Logged in as {self.user}")

    async def on_command_error(self, ctx, error):
        return
