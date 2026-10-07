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

from .config import effective_reason
from .i18n import t
from .logstore import MAX_IMAGE_BYTES, MAX_IMAGES_PER_LOG, cut, save_image_async
from .state import state
from .utils import apply_patch, fmt_duration, parse_duration

logger = logging.getLogger("mrbeast.bot")

DISCORD_MAX_TIMEOUT = timedelta(days=28)
MEDIA_DOMAINS = ("discordapp.com", "discordapp.net")
MAX_DOWNLOADS = 12
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


async def send_log(guild: discord.Guild, embed: discord.Embed):
    ch_id = state.settings.get(guild.id).get("log_channel", 0)
    if not ch_id:
        return
    ch = guild.get_channel(ch_id)
    if not ch:
        return
    perms = ch.permissions_for(guild.me)
    if not (perms.send_messages and perms.embed_links):
        logger.warning(f"Missing perms in log channel #{ch.name}")
        return
    try:
        await ch.send(embed=embed)
    except (discord.Forbidden, discord.HTTPException) as e:
        logger.error(f"Log send error: {e}")


async def apply_timeout(guild: discord.Guild, target: discord.Member, s: dict) -> Exception | None:
    timeout_td = min(timedelta(minutes=s["timeout_duration"]), DISCORD_MAX_TIMEOUT)
    try:
        await target.timeout(datetime.now(timezone.utc) + timeout_td, reason=effective_reason(s, lang()))
        return None
    except Exception as e:
        return e


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


def build_embed(source: str, target: discord.Member, s: dict, deleted: int,
                trigger_msg: discord.Message | None = None, moderator: discord.abc.User | None = None) -> discord.Embed:
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
    deleted_line = (
        t(lg, "deleted_auto", count=deleted, window=fmt_duration(s["delete_window"]))
        if auto else t(lg, "deleted_manual", count=deleted)
    )
    embed.add_field(
        name=t(lg, "action"),
        value=f"{t(lg, 'timeout_line', duration=fmt_duration(s['timeout_duration']))}\n{deleted_line}",
        inline=False,
    )
    if auto and trigger_msg is not None:
        embed.set_footer(text=f"#{trigger_msg.channel.name}")
    return embed


def person(user) -> dict:
    return {"display": cut(user.display_name), "username": cut(user.name), "id": str(user.id)}


def record_log(source: str, guild: discord.Guild, target: discord.Member, s: dict, deleted: int,
               trigger_msg: discord.Message | None = None, images: list[dict] | None = None,
               moderator: discord.abc.User | None = None):
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
        "timeout": s["timeout_duration"],
        "deleted": deleted,
        "window": s["delete_window"] if source == "auto" else None,
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
        self.processed_users = defaultdict(set)
        self.hinted: dict[int, float] = {}

    async def run_auto(self, guild: discord.Guild, target: discord.Member, trigger_msg: discord.Message, evidence: list):
        s = state.settings.get(guild.id)
        err = await apply_timeout(guild, target, s)
        if err is not None:
            if isinstance(err, discord.Forbidden):
                logger.warning(f"[auto] Cannot timeout {target}")
            else:
                logger.error(f"[auto] Timeout error: {err}")
            return
        logger.info(f"[auto] Timed out {target}")
        images = await capture_images(evidence)
        deleted = await purge_messages(guild, target, s, "auto")
        await send_log(guild, build_embed("auto", target, s, deleted, trigger_msg=trigger_msg))
        record_log("auto", guild, target, s, deleted, trigger_msg=trigger_msg, images=images)

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
        if uid in self.processed_users[gid]:
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
            self.processed_users[gid].add(uid)
            evidence = [e["msg"] for e in tracker]
            self.image_tracker[gid][uid] = []
            logger.info(f"[AutoDetect] Triggered for {message.author}")
            member = message.guild.get_member(uid)
            if member:
                asyncio.create_task(self.run_auto(message.guild, member, message, evidence))

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
        await send_log(interaction.guild, build_embed("manual", target, s, deleted, moderator=interaction.user))
        record_log("manual", interaction.guild, target, s, deleted, moderator=interaction.user)

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
        state.config.set_moderator(interaction.user.id, cut(label, 100))
        await interaction.response.send_message(t(lg, "dm_reg_ok"))

    @app_commands.command(name="log", description="Get a password reset code for the web panel (DM only)")
    @app_commands.allowed_contexts(guilds=False, dms=True, private_channels=False)
    async def log(self, interaction: discord.Interaction):
        lg = lang()
        logger.info(f"[DM] /log from {interaction.user}")
        if not state.config.moderator_id or interaction.user.id != state.config.moderator_id:
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
