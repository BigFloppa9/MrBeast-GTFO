import asyncio
import hashlib
import time

import aiohttp

from .config import CACHE_DIR, write_bytes_atomic
from .logstore import detect_extension
from .state import state
from .theme import CONTENT_TYPES

MAX_BYTES = 2 * 1024 * 1024
RETRY_AFTER = 60

lock = asyncio.Lock()
failed: dict[str, float] = {}


async def cached_image(url: str):
    name = hashlib.sha1(url.encode()).hexdigest()
    for ext in CONTENT_TYPES:
        path = CACHE_DIR / f"{name}.{ext}"
        if path.is_file():
            return path
    if time.monotonic() - failed.get(name, -RETRY_AFTER) < RETRY_AFTER:
        return None
    async with lock:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.get(url, proxy=state.proxy_url) as resp:
                    data = await resp.content.read(MAX_BYTES + 1) if resp.status == 200 else b""
        except (aiohttp.ClientError, asyncio.TimeoutError):
            data = b""
        ext = detect_extension(data) if 0 < len(data) <= MAX_BYTES else None
        if not ext:
            failed[name] = time.monotonic()
            return None
        path = CACHE_DIR / f"{name}.{ext}"
        write_bytes_atomic(path, data)
        return path
