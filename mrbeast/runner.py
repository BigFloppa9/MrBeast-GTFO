import asyncio
import logging
import math
import time

import aiohttp
import discord

from .bot import GuardBot
from .consolelog import console
from .state import state

logger = logging.getLogger("mrbeast.runner")

API_ME = "https://discord.com/api/v10/users/@me"


async def validate_token(token: str) -> tuple[bool, str]:
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(API_ME, headers={"Authorization": f"Bot {token}"}, proxy=state.proxy_url) as resp:
                if resp.status == 200:
                    return True, ""
                if resp.status == 401:
                    return False, "token_invalid"
                logger.warning(f"Token check got HTTP {resp.status} from Discord")
                return False, "token_http"
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.warning(f"Token check could not reach Discord: {e!r}")
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
        self.direct_fallback = False

    async def start(self, token: str):
        await self.stop()
        console.mark_activation()
        self.error = ""
        self.running = True
        self.stop_event = asyncio.Event()
        self.task = asyncio.create_task(self.supervise(token, self.stop_event))

    async def supervise(self, token: str, stop_event: asyncio.Event):
        delay = 5
        pool = state.proxies
        while not stop_event.is_set():
            url = None
            self.direct_fallback = False
            if pool.entries:
                url = await pool.connect(stop_event)
                self.direct_fallback = url is None
                if self.direct_fallback:
                    logger.warning("No proxy is working, trying a direct connection")
            state.proxy_url = url
            self.error = ""
            bot = GuardBot(proxy=url)
            self.bot = bot
            run = asyncio.create_task(bot.start(token))
            watch = asyncio.create_task(pool.watch() if url else pool.wait_recovery()) if (url or pool.entries) else None
            try:
                await asyncio.wait({t for t in (run, watch) if t}, return_when=asyncio.FIRST_COMPLETED)
            finally:
                if watch and not watch.done():
                    watch.cancel()
                if not bot.is_closed():
                    try:
                        await bot.close()
                    except Exception:
                        pass
            proxy_died = watch is not None and watch.done() and not watch.cancelled() and not run.done()
            result = (await asyncio.gather(run, return_exceptions=True))[0]
            if stop_event.is_set():
                break
            if proxy_died:
                logger.warning("A proxy changed state (failed, slowed down or came back), choosing the best one again")
                await pool.release()
                delay = 5
                continue
            if isinstance(result, discord.LoginFailure):
                self.error = "token_invalid"
                break
            if isinstance(result, discord.PrivilegedIntentsRequired):
                self.error = "intents"
                break
            if isinstance(result, BaseException):
                logger.error(f"Connection error: {result}")
                self.error = "network"
                if url:
                    pool.penalize()
                    await pool.release()
            if await self.pause(stop_event, delay):
                break
            delay = min(delay * 2, 60)
        state.proxy_url = None
        self.running = False

    async def pause(self, stop_event: asyncio.Event, seconds: float) -> bool:
        try:
            await asyncio.wait_for(stop_event.wait(), seconds)
            return True
        except asyncio.TimeoutError:
            return False

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
        await state.proxies.stop()

    def image_url(self, kind: str, ident: str = "") -> str | None:
        bot = self.bot
        if not bot or not bot.user:
            return None
        def asset_url(asset) -> str:
            return asset.replace(size=128, format="gif" if asset.is_animated() else "png").url

        if kind == "bot":
            return asset_url(bot.user.display_avatar)
        try:
            guild = bot.get_guild(int(ident))
        except ValueError:
            return None
        return asset_url(guild.icon) if guild and guild.icon else None

    def snapshot(self) -> dict:
        bot = self.bot
        online = bool(bot and bot.is_ready() and not bot.is_closed())
        if online:
            status = "paused" if state.config.bot_state == "paused" else "online"
            error = "proxy_failed" if self.direct_fallback else ""
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
            data["user"] = {"id": str(bot.user.id), "name": bot.user.name, "avatar": "/api/img/bot"}
            latency = bot.latency
            data["latency"] = round(latency * 1000) if math.isfinite(latency) else None
            data["uptime"] = int(time.time() - bot.ready_at) if bot.ready_at else None
            data["guilds"] = [
                {
                    "id": str(g.id),
                    "name": g.name,
                    "members": g.member_count,
                    "icon": f"/api/img/guild/{g.id}" if g.icon else None,
                }
                for g in sorted(bot.guilds, key=lambda g: g.name.lower())
            ]
        return data


runner = BotRunner()
state.runner = runner
