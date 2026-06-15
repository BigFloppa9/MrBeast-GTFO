import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import timedelta, timezone, datetime
from collections import defaultdict
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

TIMEOUT_REASON = (
    "Hello! Your account has been compromised and you have likely been banned "
    "on many servers. We strongly recommend: change your passwords on all websites "
    "you use, revoke all active Discord sessions and other apps, enable two-factor "
    "authentication, and be cautious when downloading Roblox cheats from YouTube "
    "links. If you want a clean cheat site, use weao.gg. AND NEVER SCAN RANDOM QR-codes."
)

# Persistent storage path — Railway Volume must be mounted at /data
DATA_DIR = "/data"
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# In-memory cache
log_channels: dict[int, int] = {}

image_tracker: dict = defaultdict(lambda: defaultdict(list))
processed_users: dict = defaultdict(set)

WINDOW_SECONDS = 10
MIN_IMAGES = 4
MIN_CHANNELS = 2


def load_settings():
    """Load settings from disk into memory."""
    global log_channels
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            log_channels = {int(k): int(v) for k, v in data.get("log_channels", {}).items()}
            logger.info(f"Loaded settings: {log_channels}")
        else:
            logger.info("No settings file found, starting fresh.")
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")


def save_settings():
    """Save current settings to disk."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        data = {"log_channels": {str(k): v for k, v in log_channels.items()}}
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Settings saved: {data}")
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")


async def send_log(guild: discord.Guild, embed: discord.Embed):
    log_channel_id = log_channels.get(guild.id)
    if not log_channel_id:
        logger.warning("No log channel configured.")
        return
    channel = guild.get_channel(log_channel_id)
    if not channel:
        logger.warning(f"Log channel {log_channel_id} not found in guild.")
        return
    perms = channel.permissions_for(guild.me)
    if not perms.send_messages or not perms.embed_links:
        logger.warning(f"Missing perms in log channel #{channel.name}")
        return
    try:
        await channel.send(embed=embed)
    except discord.Forbidden:
        logger.warning(f"Forbidden in log channel #{channel.name}")
    except discord.HTTPException as e:
        logger.error(f"HTTP error in log channel: {e}")


async def execute_mrbeast(
    guild: discord.Guild,
    target: discord.Member,
    trigger_message: discord.Message,
    source: str = "auto"
):
    until = datetime.now(timezone.utc) + timedelta(days=1)
    try:
        await target.timeout(until, reason=TIMEOUT_REASON)
        logger.info(f"[{source}] Timed out {target}")
    except discord.Forbidden:
        logger.warning(f"[{source}] No permission to timeout {target}")
        return
    except Exception as e:
        logger.error(f"[{source}] Timeout error: {e}")
        return

    deleted_total = 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=1)

    for channel in list(guild.text_channels) + list(guild.voice_channels):
        perms = channel.permissions_for(guild.me)
        if not perms.read_message_history or not perms.manage_messages:
            continue
        try:
            messages_to_delete = []
            async for msg in channel.history(limit=500, after=cutoff):
                if msg.author.id == target.id:
                    messages_to_delete.append(msg)
            if messages_to_delete:
                if len(messages_to_delete) == 1:
                    await messages_to_delete[0].delete()
                else:
                    await channel.delete_messages(messages_to_delete)
                deleted_total += len(messages_to_delete)
                logger.info(f"[{source}] Deleted {len(messages_to_delete)} in #{channel.name}")
        except discord.HTTPException as e:
            logger.error(f"[{source}] HTTP error in #{channel.name}: {e}")
            continue
        await asyncio.sleep(0.5)

    logger.info(f"[{source}] Total deleted: {deleted_total} for {target}")

    embed = discord.Embed(
        title="🚨 MrBeast Triggered" + (" (Auto-Detect)" if source == "auto" else " (Manual)"),
        color=discord.Color.red(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="Offender", value=f"{target.mention} (`{target.id}`)", inline=False)
    embed.add_field(
        name="Trigger message",
        value=f"[Jump to message]({trigger_message.jump_url})\n{trigger_message.content or '*[image only]*'}",
        inline=False
    )
    embed.add_field(
        name="Action",
        value=f"⏱️ Timed out for 24h\n🗑️ Deleted **{deleted_total}** messages",
        inline=False
    )
    embed.set_footer(text=f"#{trigger_message.channel.name} • {source}")
    await send_log(guild, embed)


@bot.event
async def on_ready():
    load_settings()
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if not message.guild:
        return

    has_image = any(
        att.content_type and att.content_type.startswith("image/")
        for att in message.attachments
    )
    if not has_image:
        has_image = any(e.image or e.thumbnail for e in message.embeds)
    if not has_image:
        await bot.process_commands(message)
        return

    guild_id = message.guild.id
    user_id = message.author.id

    if user_id in processed_users[guild_id]:
        await bot.process_commands(message)
        return

    now = datetime.now(timezone.utc)
    tracker = image_tracker[guild_id][user_id]
    tracker.append({"time": now, "channel_id": message.channel.id, "message": message})

    image_tracker[guild_id][user_id] = [
        e for e in tracker
        if (now - e["time"]).total_seconds() <= WINDOW_SECONDS
    ]
    tracker = image_tracker[guild_id][user_id]

    unique_channels = set(e["channel_id"] for e in tracker)
    total_images = len(tracker)
    logger.info(f"[Tracker] {message.author}: {total_images} images in {len(unique_channels)} channels")

    if total_images >= MIN_IMAGES and len(unique_channels) >= MIN_CHANNELS:
        processed_users[guild_id].add(user_id)
        image_tracker[guild_id][user_id] = []
        logger.info(f"[AutoDetect] Triggered for {message.author}")
        member = message.guild.get_member(user_id)
        if member:
            asyncio.create_task(execute_mrbeast(message.guild, member, message, source="auto"))

    await bot.process_commands(message)


@bot.tree.command(name="mrbeast", description="Timeout a compromised account for 24h and clean their messages")
@app_commands.describe(target="User to timeout (@mention or ID)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mrbeast(interaction: discord.Interaction, target: discord.Member):
    await interaction.response.defer(ephemeral=True)

    until = datetime.now(timezone.utc) + timedelta(days=1)
    try:
        await target.timeout(until, reason=TIMEOUT_REASON)
        logger.info(f"[Manual] Timed out {target}")
    except discord.Forbidden:
        await interaction.followup.send("❌ No permission to timeout this user.", ephemeral=True)
        return
    except Exception as e:
        logger.error(f"[Manual] Timeout error: {e}")
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)
        return

    deleted_total = 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=1)

    for channel in list(interaction.guild.text_channels) + list(interaction.guild.voice_channels):
        perms = channel.permissions_for(interaction.guild.me)
        if not perms.read_message_history or not perms.manage_messages:
            continue
        try:
            messages_to_delete = []
            async for msg in channel.history(limit=500, after=cutoff):
                if msg.author.id == target.id:
                    messages_to_delete.append(msg)
            if messages_to_delete:
                if len(messages_to_delete) == 1:
                    await messages_to_delete[0].delete()
                else:
                    await channel.delete_messages(messages_to_delete)
                deleted_total += len(messages_to_delete)
        except discord.HTTPException as e:
            logger.error(f"[Manual] HTTP error in #{channel.name}: {e}")
            continue
        await asyncio.sleep(0.5)

    embed = discord.Embed(
        title="🚨 MrBeast Triggered (Manual)",
        color=discord.Color.orange(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="Offender", value=f"{target.mention} (`{target.id}`)", inline=False)
    embed.add_field(name="Moderator", value=f"{interaction.user.mention}", inline=False)
    embed.add_field(
        name="Action",
        value=f"⏱️ Timed out for 24h\n🗑️ Deleted **{deleted_total}** messages",
        inline=False
    )
    await send_log(interaction.guild, embed)

    await interaction.followup.send(
        f"✅ **{target.display_name}** timed out for 24h.\n"
        f"🗑️ Deleted **{deleted_total}** messages across all channels.",
        ephemeral=True
    )


@bot.tree.command(name="mrbeastlog", description="Set the channel for MrBeast logs")
@app_commands.describe(channel="Channel to send logs to")
@app_commands.checks.has_permissions(administrator=True)
async def mrbeastlog(interaction: discord.Interaction, channel: discord.TextChannel):
    perms = channel.permissions_for(interaction.guild.me)
    missing = []
    if not perms.view_channel:
        missing.append("`View Channel`")
    if not perms.send_messages:
        missing.append("`Send Messages`")
    if not perms.embed_links:
        missing.append("`Embed Links`")

    if missing:
        try:
            await channel.set_permissions(
                interaction.guild.me,
                view_channel=True,
                send_messages=True,
                embed_links=True,
                reason="MrBeastLog: self-grant for log channel"
            )
            logger.info(f"Self-granted permissions in #{channel.name}")
        except discord.Forbidden:
            await interaction.response.send_message(
                f"❌ I can't access {channel.mention} and I also lack `Manage Channels` to fix it myself.\n\n"
                f"Please go to **{channel.name} → Edit Channel → Permissions**, add me and allow:\n"
                f"`View Channel`  `Send Messages`  `Embed Links`",
                ephemeral=True
            )
            return

    log_channels[interaction.guild.id] = channel.id
    save_settings()
    logger.info(f"Log channel set to #{channel.name} ({channel.id})")
    await interaction.response.send_message(
        f"✅ Log channel set to {channel.mention}! Saved permanently.",
        ephemeral=True
    )


bot.run(os.environ["TOKEN"])

