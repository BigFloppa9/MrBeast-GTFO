import base64
import hashlib
import hmac
import logging
import secrets
import string
import time

from cryptography.fernet import Fernet, InvalidToken

from .config import AUTH_FILE, KEY_FILE, read_json, write_bytes_atomic, write_json

logger = logging.getLogger("mrbeast.security")

PBKDF2_ITERATIONS = 400_000
MIN_PASSWORD_LENGTH = 8
CODE_ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6
CODE_TTL = 600
CODE_MAX_ATTEMPTS = 5
SESSION_TTL = 12 * 3600


def generate_code() -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))


def load_fernet() -> Fernet:
    if KEY_FILE.exists():
        key = KEY_FILE.read_bytes().strip()
    else:
        key = Fernet.generate_key()
        write_bytes_atomic(KEY_FILE, key)
    return Fernet(key)


def hash_password(password: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)


class AuthStore:
    def __init__(self):
        self.fernet = load_fernet()
        self.data = read_json(AUTH_FILE, {})
        if not isinstance(self.data, dict):
            self.data = {}

    @property
    def configured(self) -> bool:
        return bool(self.data.get("token_enc") and self.data.get("pw_hash") and self.data.get("pw_salt"))

    def save(self):
        write_json(AUTH_FILE, self.data)

    def set_token(self, token: str):
        self.data["token_enc"] = self.fernet.encrypt(token.encode("utf-8")).decode("ascii")
        self.save()

    def get_token(self) -> str | None:
        enc = self.data.get("token_enc")
        if not enc:
            return None
        try:
            return self.fernet.decrypt(enc.encode("ascii")).decode("utf-8")
        except (InvalidToken, ValueError):
            logger.error("Stored token cannot be decrypted")
            return None

    def set_password(self, password: str):
        salt = secrets.token_bytes(16)
        self.data["pw_salt"] = base64.b64encode(salt).decode("ascii")
        self.data["pw_iters"] = PBKDF2_ITERATIONS
        self.data["pw_hash"] = base64.b64encode(hash_password(password, salt)).decode("ascii")
        self.save()

    def verify_password(self, password: str) -> bool:
        try:
            salt = base64.b64decode(self.data["pw_salt"])
            expected = base64.b64decode(self.data["pw_hash"])
            iterations = int(self.data.get("pw_iters", PBKDF2_ITERATIONS))
        except (KeyError, ValueError):
            return False
        return hmac.compare_digest(hash_password(password, salt, iterations), expected)


class Sessions:
    def __init__(self):
        self.items: dict[str, float] = {}

    def create(self) -> str:
        self.prune()
        token = secrets.token_urlsafe(32)
        self.items[token] = time.time() + SESSION_TTL
        return token

    def valid(self, token: str | None) -> bool:
        if not token:
            return False
        expires = self.items.get(token)
        if expires is None:
            return False
        if expires < time.time():
            self.items.pop(token, None)
            return False
        return True

    def destroy(self, token: str | None):
        if token:
            self.items.pop(token, None)

    def clear(self):
        self.items.clear()

    def prune(self):
        now = time.time()
        for token in [t for t, e in self.items.items() if e < now]:
            self.items.pop(token, None)


class OneTimeCode:
    def __init__(self):
        self.code = ""
        self.expires = 0.0
        self.attempts = 0

    def issue(self) -> str:
        self.code = generate_code()
        self.expires = time.time() + CODE_TTL
        self.attempts = 0
        return self.code

    def active(self) -> bool:
        return bool(self.code) and self.expires > time.time()

    def remaining(self) -> int:
        return max(0, int(self.expires - time.time())) if self.active() else 0

    def clear(self):
        self.code = ""
        self.expires = 0.0
        self.attempts = 0

    def consume(self, candidate: str) -> bool:
        if not self.active():
            self.clear()
            return False
        self.attempts += 1
        if hmac.compare_digest(self.code.encode("utf-8"), (candidate or "").strip().encode("utf-8")):
            self.clear()
            return True
        if self.attempts >= CODE_MAX_ATTEMPTS:
            self.clear()
        return False


class ResetFlow:
    def __init__(self):
        self.code = OneTimeCode()
        self.open_until = 0.0
        self.tokens: dict[str, float] = {}

    def open(self):
        self.open_until = time.time() + CODE_TTL
        self.code.clear()

    def is_open(self) -> bool:
        return self.open_until > time.time()

    def issue_code(self) -> str | None:
        if not self.is_open():
            return None
        return self.code.issue()

    def verify(self, candidate: str) -> str | None:
        if not self.is_open() or not self.code.consume(candidate):
            return None
        token = secrets.token_urlsafe(24)
        self.tokens[token] = time.time() + CODE_TTL
        return token

    def redeem(self, token: str) -> bool:
        expires = self.tokens.pop(token or "", 0.0)
        if expires > time.time():
            self.open_until = 0.0
            self.tokens.clear()
            return True
        return False


class LoginLimiter:
    def __init__(self):
        self.failures: dict[str, tuple[int, float]] = {}

    def locked_for(self, key: str) -> int:
        count, until = self.failures.get(key, (0, 0.0))
        return max(0, int(until - time.time()))

    def fail(self, key: str):
        count, _ = self.failures.get(key, (0, 0.0))
        count += 1
        until = 0.0
        if count >= 5:
            until = time.time() + min(900, 30 * 2 ** (count - 5))
        self.failures[key] = (count, until)

    def reset(self, key: str):
        self.failures.pop(key, None)
