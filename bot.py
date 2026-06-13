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
    "links. If you want clear cheat site, use weao.gg. AND NEVER SCAN RANDOM QR-codes"
)

# { guild_id: channel_id }
log_channels = {}

# { guild_id: { user_id: [ {time, channel_id, message} ] } }
image_tracker = defaultdict(lambda: defaultdict(list))

# Уже обработанные юзеры чтобы не тригернуть дважды
processed_users = defaultdict(set)

WINDOW_SECONDS = 10      # окно наблюдения
MIN_IMAGES = 4           # минимум изображений
MIN_CHANNELS = 2         # минимум разных каналов

async def execute_mrbeast(guild: discord.Guild, target: discord.Member, trigger_message: discord.Message):
    """Применяет таймаут и удаляет сообщения"""
    until = datetime.now(timezone.utc) + timedelta(days=1)
    try:
        await target.timeout(until, reason=TIMEOUT_REASON)
        logger.info(f"[AutoDetect] Timed out {target}")
    except discord.Forbidden:
        logger.warning(f"[AutoDetect] No permission to timeout {target}")
        return
    except Exception as e:
        logger.error(f"[AutoDetect] Timeout error: {e}")
        return

    deleted_total = 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=1)

    for channel in guild.text_channels:
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
        except (discord.Forbidden, discord.HTTPException):
            continue
        await asyncio.sleep(0.5)

    logger.info(f"[AutoDetect] Deleted {deleted_total} messages for {target}")

    # Отправляем лог
    log_channel_id = log_channels.get(guild.id)
    if log_channel_id:
        log_channel = guild.get_channel(log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title="🚨 MrBeast Auto-Detect",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="Offender", value=f"{target.mention} (`{target.id}`)", inline=False)
            embed.add_field(name="Trigger message", value=f"[Jump]({trigger_message.jump_url})\n{trigger_message.content or '*[image]*'}", inline=False)
            embed.add_field(name="Action", value=f"⏱️ Timed out for 24h\n🗑️ Deleted {deleted_total} messages", inline=False)
            embed.set_footer(text=f"Detected in #{trigger_message.channel.name}")
            try:
                await log_channel.send(embed=embed)
            except discord.Forbidden:
                logger.warning("Cannot send to log channel")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if not message.guild:
        return

    # Проверяем есть ли изображения
    has_image = any(
        att.content_type and att.content_type.startswith("image/")
        for att in message.attachments
    )
    # Embeds с image тоже считаем
    if not has_image:
        has_image = any(e.image or e.thumbnail for e in message.embeds)

    if not has_image:
        await bot.process_commands(message)
        return

    guild_id = message.guild.id
    user_id = message.author.id

    # Если уже обработан в этой сессии — пропускаем
    if user_id in processed_users[guild_id]:
        await bot.process_commands(message)
        return

    now = datetime.now(timezone.utc)
    tracker = image_tracker[guild_id][user_id]

    # Добавляем событие
    tracker.append({
        "time": now,
        "channel_id": message.channel.id,
        "message": message
    })

    # Чистим старые события вне окна
    image_tracker[guild_id][user_id] = [
        e for e in tracker
        if (now - e["time"]).total_seconds() <= WINDOW_SECONDS
    ]
    tracker = image_tracker[guild_id][user_id]

    # Проверяем условия
    unique_channels = set(e["channel_id"] for e in tracker)
    total_images = len(tracker)

    logger.info(f"[Tracker] {message.author}: {total_images} images in {len(unique_channels)} channels")

    if total_images >= MIN_IMAGES and len(unique_channels) >= MIN_CHANNELS:
        processed_users[guild_id].add(user_id)
        image_tracker[guild_id][user_id] = []
        logger.info(f"[AutoDetect] Triggered for {message.author}")

        member = message.guild.get_member(user_id)
        if member:
            asyncio.create_task(execute_mrbeast(message.guild, member, message))

    await bot.process_commands(message)

@bot.tree.command(name="mrbeast", description="Timeout a compromised account for 24h and clean their messages")
@app_commands.describe(target="User to timeout (@mention or ID)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mrbeast(interaction: discord.Interaction, target: discord.Member):
    await interaction.response.defer(ephemeral=True)

    until = datetime.now(timezone.utc) + timedelta(days=1)
    try:
        await target.timeout(until, reason=TIMEOUT_REASON)
        logger.info(f"Timed out {target} successfully")
    except discord.Forbidden:
        await interaction.followup.send("❌ No permission to timeout this user.", ephemeral=True)
        return
    except Exception as e:
        logger.error(f"Timeout error: {e}")
        await interaction.followup.send(f"❌ Timeout error: {e}", ephemeral=True)
        return

    deleted_total = 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=1)

    for channel in interaction.guild.text_channels:
        try:
            messages_to_delete = []
            async for msg in channel.history(limit=500, after=cutoff):
                if msg.author.id == target.id:
                    messages_to_delete.append(msg)
            if messages_to_delete:
                logger.info(f"Found {len(messages_to_delete)} messages in #{channel.name}")
                if len(messages_to_delete) == 1:
                    await messages_to_delete[0].delete()
                else:
                    await channel.delete_messages(messages_to_delete)
                deleted_total += len(messages_to_delete)
        except discord.Forbidden:
            logger.warning(f"No permission in #{channel.name}")
            continue
        except discord.HTTPException as e:
            logger.error(f"HTTP error in #{channel.name}: {e}")
            continue
        await asyncio.sleep(0.5)

    await interaction.followup.send(
        f"✅ **{target.display_name}** has been timed out for 24 hours.\n"
        f"🗑️ Deleted **{deleted_total}** messages across all channels.",
        ephemeral=True
    )

@bot.tree.command(name="mrbeastlog", description="Set the channel for MrBeast auto-detect logs")
@app_commands.describe(channel="Channel to send logs to")
@app_commands.checks.has_permissions(administrator=True)
async def mrbeastlog(interaction: discord.Interaction, channel: discord.TextChannel):
    log_channels[interaction.guild.id] = channel.id
    await interaction.response.send_message(
        f"✅ Log channel set to {channel.mention}",
        ephemeral=True
    )

bot.run(os.environ["TOKEN"])
