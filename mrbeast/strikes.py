import base64
import hashlib
import json
import logging
import time

from cryptography.fernet import Fernet, InvalidToken

from .config import RETENTION_DAYS, STRIKES_FILE, write_bytes_atomic

logger = logging.getLogger("mrbeast.strikes")

DAY = 86400
EXPORT_ITERATIONS = 200_000


class StrikeStore:
    def __init__(self, fernet: Fernet):
        self.fernet = fernet
        self.data: dict[str, dict[str, dict]] = self.load()
        self.expire()

    def load(self) -> dict:
        try:
            raw = STRIKES_FILE.read_bytes()
            data = json.loads(self.fernet.decrypt(raw))
        except (OSError, InvalidToken, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    def save(self):
        try:
            payload = json.dumps(self.data, separators=(",", ":")).encode("utf-8")
            write_bytes_atomic(STRIKES_FILE, self.fernet.encrypt(payload))
        except OSError as e:
            logger.error(f"Strikes save error: {e}")

    def expire(self, reset_days: dict | None = None) -> int:
        now = time.time()
        removed = 0
        for guild_id in list(self.data):
            limit = min(RETENTION_DAYS, int((reset_days or {}).get(guild_id, RETENTION_DAYS))) * DAY
            users = self.data[guild_id]
            for user_id in list(users):
                if now - users[user_id].get("ts", 0) > limit:
                    del users[user_id]
                    removed += 1
            if not users:
                del self.data[guild_id]
        if removed:
            self.save()
        return removed

    def peek(self, guild_id: int, user_id: int, reset_days: int) -> int:
        item = self.data.get(str(guild_id), {}).get(str(user_id))
        if not item or time.time() - item.get("ts", 0) > reset_days * DAY:
            return 0
        return int(item.get("n", 0))

    def commit(self, guild_id: int, user_id: int, count: int):
        self.data.setdefault(str(guild_id), {})[str(user_id)] = {"n": count, "ts": int(time.time())}
        self.save()

    def forget(self, user_ids: set[str]) -> int:
        removed = 0
        for guild_id in list(self.data):
            for user_id in list(self.data[guild_id]):
                if user_id in user_ids:
                    del self.data[guild_id][user_id]
                    removed += 1
            if not self.data[guild_id]:
                del self.data[guild_id]
        if removed:
            self.save()
        return removed

    def export_block(self, passphrase: str) -> dict:
        salt = hashlib.sha256(str(time.time_ns()).encode()).digest()[:16]
        key = base64.urlsafe_b64encode(hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, EXPORT_ITERATIONS))
        payload = json.dumps(self.data, separators=(",", ":")).encode("utf-8")
        return {"salt": base64.b64encode(salt).decode("ascii"), "data": Fernet(key).encrypt(payload).decode("ascii")}

    def import_block(self, block: dict, passphrase: str, reset_days: dict) -> int:
        try:
            salt = base64.b64decode(block["salt"])
            key = base64.urlsafe_b64encode(hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, EXPORT_ITERATIONS))
            incoming = json.loads(Fernet(key).decrypt(str(block["data"]).encode("ascii")))
        except (KeyError, ValueError, TypeError, InvalidToken):
            raise ValueError("import_passphrase")
        if not isinstance(incoming, dict):
            raise ValueError("import_invalid")
        merged = 0
        now = time.time()
        for guild_id, users in incoming.items():
            if not isinstance(users, dict) or not str(guild_id).isdigit():
                continue
            limit = min(RETENTION_DAYS, int(reset_days.get(str(guild_id), RETENTION_DAYS))) * DAY
            for user_id, item in users.items():
                if not (str(user_id).isdigit() and isinstance(item, dict)):
                    continue
                try:
                    n, ts = int(item["n"]), int(item["ts"])
                except (KeyError, TypeError, ValueError):
                    continue
                if n < 1 or n > 1000 or now - ts > limit or ts > now + 3600:
                    continue
                current = self.data.setdefault(str(guild_id), {}).get(str(user_id))
                if current is None or current.get("ts", 0) < ts:
                    self.data[str(guild_id)][str(user_id)] = {"n": n, "ts": ts}
                    merged += 1
        self.save()
        return merged
