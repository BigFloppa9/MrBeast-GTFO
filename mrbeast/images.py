import asyncio
import hashlib
import time

import aiohttp

from .config import CACHE_DIR, write_bytes_atomic
from .logstore import detect_extension, image_complete
from .state import state
from .utils import read_capped
from .theme import CONTENT_TYPES

MAX_BYTES = 8 * 1024 * 1024
RETRY_AFTER = 60

lock = asyncio.Lock()
failed: dict[str, float] = {}
verified: set[str] = set()


async def cached_image(url: str):
    name = hashlib.sha1(url.encode()).hexdigest()
    for ext in CONTENT_TYPES:
        path = CACHE_DIR / f"{name}.{ext}"
        if not path.is_file():
            continue
        if name in verified:
            return path
        try:
            good = image_complete(path.read_bytes())
        except OSError:
            good = False
        if good:
            verified.add(name)
            return path
        path.unlink(missing_ok=True)
    if time.monotonic() - failed.get(name, -RETRY_AFTER) < RETRY_AFTER:
        return None
    async with lock:
        async def fetch(route):
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20, connect=8)) as session:
                async with session.get(url, proxy=route) as resp:
                    if resp.status != 200:
                        raise aiohttp.ClientError(f"HTTP {resp.status}")
                    return await read_capped(resp, MAX_BYTES)

        try:
            data = await state.proxies.with_routes(fetch, direct_first=False, limit=2)
        except Exception:
            data = b""
        ext = detect_extension(data) if 0 < len(data) <= MAX_BYTES and image_complete(data) else None
        if not ext:
            failed[name] = time.monotonic()
            return None
        path = CACHE_DIR / f"{name}.{ext}"
        write_bytes_atomic(path, data)
        verified.add(name)
        return path
