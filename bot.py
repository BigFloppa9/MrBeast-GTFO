import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import timedelta, timezone, datetime
from collections import defaultdict
import os, json, logging, re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "/data/settings.json"
DISCORD_MAX_TIMEOUT = timedelta(days=28)

settings: dict = {}
image_tracker: dict = defaultdict(lambda: defaultdict(list))
processed_users: dict = defaultdict(set)

DEFAULT_SETTINGS = {
    "timeout_reason": (
        "Hello! Your account has been compromised and you have likely been banned "
        "on many servers. We strongly recommend: change your passwords on all websites "
        "you use, revoke all active Discord sessions and other apps, enable two-factor "
        "authentication, and be cautious when downloading Roblox cheats from YouTube "
        "links. If you want a clean cheat site, use weao.gg. AND NEVER SCAN RANDOM QR-codes."
    ),
    "timeout_duration": 1440,
    "delete_window": 1440,
    "log_channel": 0,
    "auto_min_images": 4,
    "auto_min_channels": 2,
    "auto_window_seconds": 10,
}


def guild_settings(guild_id: int) -> dict:
    if guild_id not in settings:
        settings[guild_id] = DEFAULT_SETTINGS.copy()
    return settings[guild_id]


def load_settings():
    global settings
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE) as f:
                settings = {int(k): v for k, v in json.load(f).items()}
            logger.info(f"Settings loaded: {len(settings)} guilds")
    except Exception as e:
        logger.error(f"Load error: {e}")


def save_settings():
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump({str(k): v for k, v in settings.items()}, f, indent=2)
    except Exception as e:
        logger.error(f"Save error: {e}")


def parse_duration(s: str) -> timedelta | None:
    total = 0
    for val, unit in re.findall(r"(\d+)([dhm])", s.lower()):
        match unit:
            case "d": total += int(val) * 1440
            case "h": total += int(val) * 60
            case "m": total += int(val)
    return timedelta(minutes=total) if total > 0 else None


def fmt_duration(minutes: int) -> str:
    d, rem = divmod(minutes, 1440)
    h, m = divmod(rem, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    return " ".join(parts) or "0m"


async def send_log(guild: discord.Guild, embed: discord.Embed):
    ch_id = guild_settings(guild.id).get("log_channel", 0)
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


async def do_mrbeast(guild: discord.Guild, target: discord.Member, trigger_msg: discord.Message, source: str = "auto"):
    s = guild_settings(guild.id)
    timeout_td = timedelta(minutes=s["timeout_duration"])
    if timeout_td > DISCORD_MAX_TIMEOUT:
        timeout_td = DISCORD_MAX_TIMEOUT

    try:
        await target.timeout(datetime.now(timezone.utc) + timeout_td, reason=s["timeout_reason"])
        logger.info(f"[{source}] Timed out {target}")
    except discord.Forbidden:
        logger.warning(f"[{source}] Cannot timeout {target}")
        return
    except Exception as e:
        logger.error(f"[{source}] Timeout error: {e}")
        return

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
                if len(msgs) == 1:
                    await msgs[0].delete()
                else:
                    await ch.delete_messages(msgs)
                deleted += len(msgs)
                logger.info(f"[{source}] Deleted {len(msgs)} in #{ch.name}")
        except discord.HTTPException as e:
            logger.error(f"[{source}] Error in #{ch.name}: {e}")
        await asyncio.sleep(0.5)

    logger.info(f"[{source}] Total deleted: {deleted} for {target}")

    embed = discord.Embed(
        title=f"🚨 MrBeast {'(Auto)' if source == 'auto' else '(Manual)'}",
        color=discord.Color.red() if source == "auto" else discord.Color.orange(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="Offender", value=f"{target.mention} (`{target.id}`)", inline=False)
    embed.add_field(name="Trigger", value=f"[Jump]({trigger_msg.jump_url})\n{trigger_msg.content or '*[image]*'}", inline=False)
    embed.add_field(name="Action", value=f"⏱️ Timeout: {fmt_duration(s['timeout_duration'])}\n🗑️ Deleted {deleted} messages (last {fmt_duration(s['delete_window'])})", inline=False)
    if source == "auto":
        embed.set_footer(text=f"#{trigger_msg.channel.name}")
    await send_log(guild, embed)


@bot.event
async def on_ready():
    load_settings()
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return

    has_image = (
        any(a.content_type and a.content_type.startswith("image/") for a in message.attachments)
        or any(e.image or e.thumbnail for e in message.embeds)
    )

    if has_image:
        gid, uid = message.guild.id, message.author.id
        if uid not in processed_users[gid]:
            s = guild_settings(gid)
            now = datetime.now(timezone.utc)
            tracker = image_tracker[gid][uid]
            tracker.append({"time": now, "ch": message.channel.id, "msg": message})
            image_tracker[gid][uid] = [e for e in tracker if (now - e["time"]).total_seconds() <= s["auto_window_seconds"]]
            tracker = image_tracker[gid][uid]

            unique_chs = {e["ch"] for e in tracker}
            logger.info(f"[Tracker] {message.author}: {len(tracker)} images in {len(unique_chs)} channels")

            if len(tracker) >= s["auto_min_images"] and len(unique_chs) >= s["auto_min_channels"]:
                processed_users[gid].add(uid)
                image_tracker[gid][uid] = []
                logger.info(f"[AutoDetect] Triggered for {message.author}")
                member = message.guild.get_member(uid)
                if member:
                    asyncio.create_task(do_mrbeast(message.guild, member, message, "auto"))

    await bot.process_commands(message)


@bot.tree.command(name="mrbeast", description="Timeout a compromised account and delete their messages")
@app_commands.describe(target="User to timeout (@mention or ID)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mrbeast(interaction: discord.Interaction, target: discord.Member):
    await interaction.response.defer(ephemeral=True)
    s = guild_settings(interaction.guild.id)

    timeout_td = timedelta(minutes=s["timeout_duration"])
    if timeout_td > DISCORD_MAX_TIMEOUT:
        timeout_td = DISCORD_MAX_TIMEOUT

    try:
        await target.timeout(datetime.now(timezone.utc) + timeout_td, reason=s["timeout_reason"])
    except discord.Forbidden:
        await interaction.followup.send("❌ No permission to timeout this user.", ephemeral=True)
        return
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)
        return

    deleted = 0
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=s["delete_window"])
    all_channels = list(interaction.guild.text_channels) + list(interaction.guild.voice_channels)

    for ch in all_channels:
        perms = ch.permissions_for(interaction.guild.me)
        if not (perms.read_message_history and perms.manage_messages):
            continue
        try:
            msgs = [m async for m in ch.history(limit=500, after=cutoff) if m.author.id == target.id]
            if msgs:
                if len(msgs) == 1:
                    await msgs[0].delete()
                else:
                    await ch.delete_messages(msgs)
                deleted += len(msgs)
        except discord.HTTPException as e:
            logger.error(f"[Manual] Error in #{ch.name}: {e}")
        await asyncio.sleep(0.5)

    dummy = await interaction.original_response()
    embed = discord.Embed(title="🚨 MrBeast (Manual)", color=discord.Color.orange(), timestamp=datetime.now(timezone.utc))
    embed.add_field(name="Offender", value=f"{target.mention} (`{target.id}`)", inline=False)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
    embed.add_field(name="Action", value=f"⏱️ Timeout: {fmt_duration(s['timeout_duration'])}\n🗑️ Deleted {deleted} messages", inline=False)
    await send_log(interaction.guild, embed)

    await interaction.followup.send(
        f"✅ **{target.display_name}** timed out for {fmt_duration(s['timeout_duration'])}.\n"
        f"🗑️ Deleted **{deleted}** messages (last {fmt_duration(s['delete_window'])}).",
        ephemeral=True
    )


@bot.tree.command(name="mrbeastlog", description="Set the log channel for MrBeast actions")
@app_commands.describe(channel="Channel to send logs to")
@app_commands.checks.has_permissions(administrator=True)
async def mrbeastlog(interaction: discord.Interaction, channel: discord.TextChannel):
    perms = channel.permissions_for(interaction.guild.me)
    missing = [p for p, v in [("View Channel", perms.view_channel), ("Send Messages", perms.send_messages), ("Embed Links", perms.embed_links)] if not v]

    if missing:
        try:
            await channel.set_permissions(interaction.guild.me, view_channel=True, send_messages=True, embed_links=True, reason="MrBeastLog self-grant")
        except discord.Forbidden:
            await interaction.response.send_message(
                f"❌ Missing permissions in {channel.mention}: `{'` `'.join(missing)}`\n"
                f"Go to **{channel.name} → Edit Channel → Permissions** and allow me these.",
                ephemeral=True
            )
            return

    guild_settings(interaction.guild.id)["log_channel"] = channel.id
    save_settings()
    await interaction.response.send_message(f"✅ Log channel set to {channel.mention}!", ephemeral=True)


@bot.tree.command(name="mrbeastconfig", description="Configure MrBeast bot settings")
@app_commands.describe(
    reason="Timeout reason shown to users (leave empty to keep current)",
    timeout="Timeout duration, e.g. 1d / 12h / 30m / 1d12h (max 28d)",
    deletetime="How far back to delete messages, e.g. 24h / 7d / 30m",
)
@app_commands.checks.has_permissions(administrator=True)
async def mrbeastconfig(
    interaction: discord.Interaction,
    reason: str = None,
    timeout: str = None,
    deletetime: str = None,
):
    s = guild_settings(interaction.guild.id)
    changes = []
    errors = []

    if reason is not None:
        s["timeout_reason"] = reason
        changes.append(f"📝 Reason updated")

    if timeout is not None:
        td = parse_duration(timeout)
        if td is None:
            errors.append(f"❌ Invalid timeout format `{timeout}`. Use: `1d`, `12h`, `30m`, `1d12h` (max `28d`)")
        elif td > DISCORD_MAX_TIMEOUT:
            errors.append(f"❌ Timeout too long. Discord maximum is **28d**.")
        elif td.total_seconds() < 60:
            errors.append(f"❌ Timeout too short. Minimum is **1m**.")
        else:
            s["timeout_duration"] = int(td.total_seconds() // 60)
            changes.append(f"⏱️ Timeout set to **{fmt_duration(s['timeout_duration'])}**")

    if deletetime is not None:
        td = parse_duration(deletetime)
        if td is None:
            errors.append(f"❌ Invalid deletetime format `{deletetime}`. Use: `24h`, `7d`, `30m`")
        elif td.total_seconds() < 60:
            errors.append(f"❌ Delete window too short. Minimum is **1m**.")
        else:
            s["delete_window"] = int(td.total_seconds() // 60)
            changes.append(f"🗑️ Delete window set to **{fmt_duration(s['delete_window'])}**")

    if errors:
        await interaction.response.send_message("\n".join(errors), ephemeral=True)
        return

    if not changes:
        await interaction.response.send_message(
            f"**Current config:**\n"
            f"⏱️ Timeout: `{fmt_duration(s['timeout_duration'])}`\n"
            f"🗑️ Delete window: `{fmt_duration(s['delete_window'])}`\n"
            f"📝 Reason: {s['timeout_reason'][:100]}{'...' if len(s['timeout_reason']) > 100 else ''}",
            ephemeral=True
        )
        return

    save_settings()
    await interaction.response.send_message("\n".join(changes), ephemeral=True)


bot.run(os.environ["TOKEN"])
