import base64
import hashlib
import json
import time

from cryptography.fernet import Fernet, InvalidToken

ITERATIONS = 200000


def derive(passphrase: str, salt: bytes) -> bytes:
    return base64.urlsafe_b64encode(hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, ITERATIONS))


def seal(payload, passphrase: str) -> dict:
    salt = hashlib.sha256(str(time.time_ns()).encode()).digest()[:16]
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return {"salt": base64.b64encode(salt).decode("ascii"), "data": Fernet(derive(passphrase, salt)).encrypt(body).decode("ascii")}


def unseal(block, passphrase: str):
    try:
        salt = base64.b64decode(block["salt"])
        return json.loads(Fernet(derive(passphrase, salt)).decrypt(str(block["data"]).encode("ascii")))
    except (KeyError, ValueError, TypeError, InvalidToken):
        raise ValueError("import_passphrase")
