import asyncio
import base64
import json
import logging
import re
from urllib.parse import unquote

import aiohttp
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from .config import CACHE_DIR, read_json, write_json

logger = logging.getLogger("mrbeast.happ")

KEYS_URL = "https://raw.githubusercontent.com/cylaro/happ-decrypt/29c299d03db63a9f0a510a48166f784b0fcb4b2a/public/data/crypt5-keys.json"
KEYS_SOURCE = "github.com/cylaro/happ-decrypt"
KEYS_FILE = CACHE_DIR / "happ-crypt5-keys.json"
MAX_KEYS_BYTES = 400_000
MARKER = re.compile(r"^[A-Za-z0-9._~-]{8}$")

keys_lock = asyncio.Lock()
key_cache: dict = {}


class CryptError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def b64_bytes(text: bytes | str) -> bytes:
    raw = text.decode("latin-1") if isinstance(text, bytes) else text
    clean = re.sub(r"\s", "", raw).replace("-", "+").replace("_", "/").rstrip("=")
    clean += "=" * (-len(clean) % 4)
    try:
        return base64.b64decode(clean, validate=True)
    except ValueError:
        raise CryptError("crypt_failed")


def swap_adjacent(data: bytes) -> bytes:
    out = bytearray(data)
    for i in range(0, len(out) - 1, 2):
        out[i], out[i + 1] = out[i + 1], out[i]
    return bytes(out)


def swap_halves(data: bytes) -> bytes:
    out = bytearray(data)
    for i in range(0, len(out) - len(out) % 4, 4):
        out[i], out[i + 2] = out[i + 2], out[i]
        out[i + 1], out[i + 3] = out[i + 3], out[i + 1]
    return bytes(out)


def private_key(marker: str, table: dict):
    value = table.get(marker)
    if not isinstance(value, str) or not value:
        raise CryptError("crypt_unknown_key")
    if marker not in key_cache:
        try:
            key_cache[marker] = serialization.load_der_private_key(base64.b64decode(value), password=None)
        except (ValueError, TypeError):
            raise CryptError("crypt_failed")
    return key_cache[marker]


def decrypt_body(body: bytes, key, salted: bool) -> str:
    if len(body) < 13:
        raise CryptError("crypt_failed")
    nonce, salt, start = body[:12], None, 12
    if salted:
        if len(body) < 22:
            raise CryptError("crypt_failed")
        salt, start = body[14:22], 22
    end = start
    while end < len(body) and 48 <= body[end] <= 57:
        end += 1
    if end == start:
        raise CryptError("crypt_failed")
    length = int(body[start:end])
    packed = body[end:]
    if not packed or length > len(packed) - 1:
        raise CryptError("crypt_failed")
    encrypted_url = packed[1:length + 1]
    rsa_cipher = b64_bytes(packed[length + 1:])
    try:
        rsa_plain = key.decrypt(rsa_cipher, padding.PKCS1v15())
    except ValueError:
        raise CryptError("crypt_failed")
    chacha_key = bytearray(b64_bytes(swap_adjacent(rsa_plain)))
    if len(chacha_key) != 32:
        raise CryptError("crypt_failed")
    if salt:
        for i in range(32):
            chacha_key[i] ^= salt[i % len(salt)]
    try:
        inner = ChaCha20Poly1305(bytes(chacha_key)).decrypt(nonce, b64_bytes(encrypted_url), None)
    except Exception:
        raise CryptError("crypt_failed")
    try:
        return b64_bytes(swap_adjacent(inner)).decode("utf-8")
    except UnicodeDecodeError:
        raise CryptError("crypt_failed")


def decrypt_crypt5(payload: str, table: dict) -> str:
    payload = payload.strip()
    if "%" in payload:
        payload = unquote(payload)
    shuffled = swap_halves(re.sub(r"\s", "", payload).encode("utf-8"))
    if len(shuffled) < 8:
        raise CryptError("crypt_failed")
    marker = (shuffled[:4] + shuffled[-4:]).decode("latin-1")
    if not MARKER.match(marker):
        raise CryptError("crypt_failed")
    key = private_key(marker, table)
    body = shuffled[4:-4]
    prefer_salted = len(body) > 12 and not 48 <= body[12] <= 57
    first = None
    for salted in (prefer_salted, not prefer_salted):
        try:
            return decrypt_body(body, key, salted)
        except CryptError as e:
            first = first or e
    raise first


def valid_table(data) -> bool:
    return (
        isinstance(data, dict) and 0 < len(data) <= 200
        and all(isinstance(k, str) and MARKER.match(k) and isinstance(v, str) and 100 < len(v) < 20000 for k, v in data.items())
    )


async def keytable(via: str | None = None) -> dict:
    async with keys_lock:
        data = read_json(KEYS_FILE, None)
        if valid_table(data):
            return data
        try:
            timeout = aiohttp.ClientTimeout(total=25)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(KEYS_URL, proxy=via) as resp:
                    if resp.status != 200:
                        raise CryptError("crypt_keys_unavailable")
                    raw = await resp.content.read(MAX_KEYS_BYTES + 1)
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError):
            raise CryptError("crypt_keys_unavailable")
        if len(raw) > MAX_KEYS_BYTES:
            raise CryptError("crypt_keys_unavailable")
        try:
            data = json.loads(raw)
        except ValueError:
            raise CryptError("crypt_keys_unavailable")
        if not valid_table(data):
            raise CryptError("crypt_keys_unavailable")
        write_json(KEYS_FILE, data)
        return data


async def resolve(link: str, via: str | None = None) -> str:
    payload = link.split("/", 3)[3] if link.count("/") >= 3 else ""
    table = await keytable(via)
    try:
        url = await asyncio.to_thread(decrypt_crypt5, payload, table)
    except CryptError as e:
        if e.code == "crypt_unknown_key" and KEYS_FILE.exists():
            KEYS_FILE.unlink(missing_ok=True)
            table = await keytable(via)
            url = await asyncio.to_thread(decrypt_crypt5, payload, table)
        else:
            raise
    if not url.lower().startswith(("http://", "https://")):
        raise CryptError("crypt_failed")
    return url.strip()
