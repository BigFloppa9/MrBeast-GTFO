import asyncio
import logging
import math
import time

import aiohttp
import discord

from .bot import GuardBot
from .state import state

logger = logging.getLogger("mrbeast.runner")

API_ME = "https://discord.com/api/v10/users/@me"


async def validate_token(token: str) -> tuple[bool, str]:
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(API_ME, headers={"Authorization": f"Bot {token}"}) as resp:
                if resp.status == 200:
                    return True, ""
                if resp.status == 401:
                    return False, "token_invalid"
                return False, "token_http"
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return False, "token_network"


def clean_token(raw: str) -> str:
    token = (raw or "").strip()
    if token.lower().startswith("bot "):
        token = token[4:].strip()
    return token


class BotRunner:
    def __init__(self):
        self.bot: GuardBot | None = None
        self.task: asyncio.Task | None = None
        self.stop_event: asyncio.Event | None = None
        self.error = ""
        self.running = False

    async def start(self, token: str):
        await self.stop()
        self.error = ""
        self.running = True
        self.stop_event = asyncio.Event()
        self.task = asyncio.create_task(self.supervise(token, self.stop_event))

    async def supervise(self, token: str, stop_event: asyncio.Event):
        delay = 5
        while not stop_event.is_set():
            bot = GuardBot()
            self.bot = bot
            try:
                await bot.start(token)
                if stop_event.is_set():
                    break
            except discord.LoginFailure:
                self.error = "token_invalid"
                break
            except discord.PrivilegedIntentsRequired:
                self.error = "intents"
                break
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error(f"Connection error: {e}")
                self.error = "network"
            finally:
                if not bot.is_closed():
                    try:
                        await bot.close()
                    except Exception:
                        pass
            try:
                await asyncio.wait_for(stop_event.wait(), delay)
            except asyncio.TimeoutError:
                delay = min(delay * 2, 60)
        self.running = False

    async def stop(self):
        task, bot, event = self.task, self.bot, self.stop_event
        self.task = None
        if event:
            event.set()
        if bot and not bot.is_closed():
            try:
                await bot.close()
            except Exception as e:
                logger.error(f"Close error: {e}")
        if task:
            done, _ = await asyncio.wait({task}, timeout=10)
            if not done:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
        self.bot = None
        self.running = False

    def snapshot(self) -> dict:
        bot = self.bot
        online = bool(bot and bot.is_ready() and not bot.is_closed())
        if online:
            status = "online"
            error = ""
        elif self.running and self.error == "network":
            status = "reconnecting"
            error = self.error
        elif self.error:
            status = "error"
            error = self.error
        elif self.running:
            status = "starting"
            error = ""
        else:
            status = "stopped"
            error = ""
        data = {"status": status, "error": error, "user": None, "latency": None, "uptime": None, "guilds": []}
        if online and bot.user:
            avatar = bot.user.display_avatar.replace(size=128, format="png").url
            data["user"] = {"id": str(bot.user.id), "name": bot.user.name, "avatar": avatar}
            latency = bot.latency
            data["latency"] = round(latency * 1000) if math.isfinite(latency) else None
            data["uptime"] = int(time.time() - bot.ready_at) if bot.ready_at else None
            data["guilds"] = [
                {
                    "id": str(g.id),
                    "name": g.name,
                    "members": g.member_count,
                    "icon": g.icon.replace(size=64, format="png").url if g.icon else None,
                }
                for g in sorted(bot.guilds, key=lambda g: g.name.lower())
            ]
        return data


runner = BotRunner()
state.runner = runner
