import asyncio
import hashlib
import logging
import os
import re
import time

from .config import IMAGES_DIR, LOGS_FILE, ensure_dirs, read_json, write_bytes_atomic, write_json

logger = logging.getLogger("mrbeast.logs")

MAX_LOGS = 300
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_IMAGES_PER_LOG = 8
FIELD_LIMIT = 69
IMAGE_NAME = re.compile(r"^[0-9a-f]{64}\.(png|jpg|gif|webp)$")


def cut(text, limit: int = FIELD_LIMIT) -> str:
    text = str(text or "")
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def detect_extension(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def store_image(data: bytes) -> str | None:
    if not data or len(data) > MAX_IMAGE_BYTES:
        return None
    ext = detect_extension(data)
    if not ext:
        return None
    name = f"{hashlib.sha256(data).hexdigest()}.{ext}"
    path = IMAGES_DIR / name
    if path.exists():
        os.utime(path, None)
    else:
        write_bytes_atomic(path, data)
    return name


def image_path(name: str):
    if not IMAGE_NAME.match(name or ""):
        return None
    path = IMAGES_DIR / name
    return path if path.is_file() else None


class LogStore:
    def __init__(self):
        raw = read_json(LOGS_FILE, {})
        entries = raw.get("logs") if isinstance(raw, dict) else None
        self.entries: list[dict] = entries if isinstance(entries, list) else []
        self.last_id = max([e.get("id", 0) for e in self.entries] + [0])
        self.cleanup_images()

    def add(self, entry: dict) -> dict:
        entry_id = max(self.last_id + 1, int(time.time() * 1000))
        self.last_id = entry_id
        entry["id"] = entry_id
        entry["ts"] = time.time()
        self.entries.append(entry)
        pruned = False
        while len(self.entries) > MAX_LOGS:
            self.entries.pop(0)
            pruned = True
        self.save()
        if pruned:
            self.cleanup_images()
        return entry

    def since(self, after: int = 0) -> list[dict]:
        return [e for e in self.entries if e["id"] > after]

    def save(self):
        try:
            write_json(LOGS_FILE, {"logs": self.entries})
        except OSError as e:
            logger.error(f"Log save error: {e}")

    def cleanup_images(self):
        ensure_dirs()
        used = set()
        for entry in self.entries:
            trigger = entry.get("trigger") or {}
            for image in trigger.get("images", []):
                used.add(image.get("file"))
        try:
            fresh = time.time() - 300
            for path in IMAGES_DIR.iterdir():
                if path.name not in used and path.stat().st_mtime < fresh:
                    path.unlink(missing_ok=True)
        except OSError as e:
            logger.error(f"Image cleanup error: {e}")


async def save_image_async(data: bytes) -> str | None:
    return await asyncio.to_thread(store_image, data)
