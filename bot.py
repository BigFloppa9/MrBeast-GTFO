import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import timedelta, timezone, datetime
from collections import defaultdict
import os
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

log_channels: dict[int, int] = {}
image_tracker: dict = defaultdict(lambda: defaultdict(list))
processed_users: dict = defaultdict(set)

WINDOW_SECONDS = 10
MIN_IMAGES = 4
MIN_CHANNELS = 2


async def send_log(guild: discord.Guild, embed: discord.Embed):
    log_channel_id = log_channels.get(guild.id)
    if not log_channel_id:
        log_channel_id = int(os.environ.get("LOG_CHANNEL_ID", 0))
    if not log_channel_id:
        logger.warning("No log channel configured.")
        return
    channel = guild.get_channel(log_channel_id)
    if not channel:
        logger.warning(f"Log channel {log_channel_id} not found.")
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

    for channel in guild.text_channels:
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
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")
    env_log = int(os.environ.get("LOG_CHANNEL_ID", 0))
    if env_log:
        for guild in bot.guilds:
            if guild.id not in log_channels:
                log_channels[guild.id] = env_log
        logger.info(f"Loaded LOG_CHANNEL_ID={env_log} from env")


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

    for channel in interaction.guild.text_channels:
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
        missing.append("view_channel")
    if not perms.send_messages:
        missing.append("send_messages")
    if not perms.embed_links:
        missing.append("embed_links")

    if missing:
        # Try to grant ourselves access via channel overwrite
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
    logger.info(f"Log channel set to #{channel.name} ({channel.id})")
    await interaction.response.send_message(
        f"✅ Log channel set to {channel.mention}!\n"
        f"⚠️ To survive bot restarts, add this to Railway Variables:\n"
        f"`LOG_CHANNEL_ID` = `{channel.id}`",
        ephemeral=True
    )


@bot.tree.command(name="mrbeasttest", description="Diagnose bot permissions in a channel")
@app_commands.describe(channel="Channel to check (leave empty for current channel)")
@app_commands.checks.has_permissions(administrator=True)
async def mrbeasttest(interaction: discord.Interaction, channel: discord.TextChannel = None):
    target = channel or interaction.channel
    perms = target.permissions_for(interaction.guild.me)

    def s(b): return "✅" if b else "❌"

    log_id = log_channels.get(interaction.guild.id) or int(os.environ.get("LOG_CHANNEL_ID", 0))

    report = (
        f"**Permission check for {target.mention}:**\n"
        f"{s(perms.view_channel)} View Channel\n"
        f"{s(perms.send_messages)} Send Messages\n"
        f"{s(perms.embed_links)} Embed Links\n"
        f"{s(perms.read_message_history)} Read Message History\n"
        f"{s(perms.manage_messages)} Manage Messages\n"
        f"{s(perms.manage_channels)} Manage Channels (needed for self-grant)\n"
        f"{s(perms.moderate_members)} Moderate Members\n\n"
        f"**Current log channel:** " + (f"<#{log_id}>" if log_id else "❌ not set")
    )

    await interaction.response.send_message(report, ephemeral=True)


bot.run(os.environ["TOKEN"])
