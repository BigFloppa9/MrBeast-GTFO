import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import timedelta, timezone, datetime
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

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="mrbeast", description="Timeout a compromised account for 24h and clean their messages")
@app_commands.describe(target="User to timeout (@mention or ID)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mrbeast(interaction: discord.Interaction, target: discord.Member):
    await interaction.response.defer(ephemeral=True)

    # Apply 24h timeout
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

    # Delete messages across all channels (last 24h)
    deleted_total = 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=1)

    logger.info(f"Starting message deletion for {target} across {len(interaction.guild.text_channels)} channels")

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
                logger.info(f"Deleted {len(messages_to_delete)} messages in #{channel.name}")
            else:
                logger.info(f"No messages found in #{channel.name}")

        except discord.Forbidden:
            logger.warning(f"No permission in #{channel.name} — skipping")
            continue
        except discord.HTTPException as e:
            logger.error(f"HTTP error in #{channel.name}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error in #{channel.name}: {e}")
            continue

        await asyncio.sleep(0.5)

    logger.info(f"Total deleted: {deleted_total}")

    await interaction.followup.send(
        f"✅ **{target.display_name}** has been timed out for 24 hours.\n"
        f"🗑️ Deleted **{deleted_total}** messages across all channels.",
        ephemeral=True
    )

bot.run(os.environ["TOKEN"])
