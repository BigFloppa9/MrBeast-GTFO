import asyncio
import time

import aiohttp

from .config import DATA_DIR, write_bytes_atomic
from .logstore import MAX_IMAGE_BYTES, detect_extension

KOS_URL = (
    "https://sun1-13.userapi.com/s/v1/ig2/6ik4I-I0a9zOuDvPmcE45LYfduxHpbV2E2WexX5hHhrxVSPn-iaon8XhyfC0LDViMa0lCd_KDBoi2zKITAiR_RfY.jpg"
    "?quality=95&as=32x17,48x25,72x38,108x57,160x85,240x127,360x191,480x255,540x287,640x340,720x382,968x514&from=bu&cs=968x0"
)
CONTENT_TYPES = {"png": "image/png", "jpg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}
RETRY_AFTER = 60

lock = asyncio.Lock()
failed_at = 0.0


def cached():
    for ext in CONTENT_TYPES:
        path = DATA_DIR / f"kos-bg.{ext}"
        if path.is_file():
            return path
    return None


async def ensure_background():
    global failed_at
    path = cached()
    if path or time.monotonic() - failed_at < RETRY_AFTER:
        return path
    async with lock:
        path = cached()
        if path:
            return path
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.get(KOS_URL) as resp:
                    data = await resp.content.read(MAX_IMAGE_BYTES + 1) if resp.status == 200 else b""
        except (aiohttp.ClientError, asyncio.TimeoutError):
            data = b""
        ext = detect_extension(data) if 0 < len(data) <= MAX_IMAGE_BYTES else None
        if not ext:
            failed_at = time.monotonic()
            return None
        path = DATA_DIR / f"kos-bg.{ext}"
        write_bytes_atomic(path, data)
        return path
