import asyncio
import hashlib
import json
import logging
import os
import re
import time

from cryptography.fernet import Fernet, InvalidToken

from .config import IMAGES_DIR, LOGS_FILE, ensure_dirs, write_bytes_atomic

logger = logging.getLogger("mrbeast.logs")

MAX_LOGS = 300
MAX_AGE = 30 * 86400
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_IMAGES_PER_LOG = 8
FIELD_LIMIT = 69
IMAGE_NAME = re.compile(r"^[0-9a-f]{64}\.(png|jpg|gif|webp)$")

cipher: Fernet | None = None


def set_cipher(value: Fernet):
    global cipher
    cipher = value


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
        write_bytes_atomic(path, cipher.encrypt(data))
    return name


def read_image(name: str) -> bytes | None:
    path = image_path(name)
    if path is None:
        return None
    try:
        return cipher.decrypt(path.read_bytes())
    except (OSError, InvalidToken):
        return None


def image_path(name: str):
    if not IMAGE_NAME.match(name or ""):
        return None
    path = IMAGES_DIR / name
    return path if path.is_file() else None


class LogStore:
    def __init__(self, fernet: Fernet):
        set_cipher(fernet)
        self.entries: list[dict] = self.load()
        self.last_id = max([e.get("id", 0) for e in self.entries] + [0])
        if not self.expire():
            self.cleanup_images()

    def load(self) -> list[dict]:
        try:
            raw = LOGS_FILE.read_bytes()
        except OSError:
            return []
        try:
            raw = cipher.decrypt(raw)
        except InvalidToken:
            pass
        try:
            data = json.loads(raw)
        except ValueError:
            return []
        entries = data.get("logs") if isinstance(data, dict) else None
        return entries if isinstance(entries, list) else []

    def expire(self) -> bool:
        cutoff = time.time() - MAX_AGE
        kept = [e for e in self.entries if e.get("ts", 0) >= cutoff]
        if len(kept) == len(self.entries):
            return False
        self.entries = kept
        self.save()
        self.cleanup_images()
        return True

    def add(self, entry: dict) -> dict:
        entry_id = max(self.last_id + 1, int(time.time() * 1000))
        self.last_id = entry_id
        entry["id"] = entry_id
        entry["ts"] = time.time()
        self.entries.append(entry)
        self.expire()
        pruned = False
        while len(self.entries) > MAX_LOGS:
            self.entries.pop(0)
            pruned = True
        self.save()
        if pruned:
            self.cleanup_images()
        return entry

    def since(self, after: int = 0) -> list[dict]:
        self.expire()
        return [e for e in self.entries if e["id"] > after]

    def save(self):
        try:
            payload = json.dumps({"logs": self.entries}, ensure_ascii=False).encode("utf-8")
            write_bytes_atomic(LOGS_FILE, cipher.encrypt(payload))
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
