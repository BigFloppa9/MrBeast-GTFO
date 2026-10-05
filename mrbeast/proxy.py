import asyncio
import copy
import hashlib
import io
import json
import logging
import os
import platform
import re
import secrets
import shutil
import signal
import socket
import time
import uuid
import zipfile
from urllib.parse import parse_qs, unquote, urlsplit

import aiohttp
from cryptography.fernet import Fernet, InvalidToken

from .config import BIN_DIR, PROXIES_FILE, XRAY_DIR, ensure_dirs, write_bytes_atomic, write_json

logger = logging.getLogger("mrbeast.proxy")

MAX_PROXIES = 100
MAX_LINE = 8000
PROBE_URL = "https://discord.com/api/v10/gateway"
XRAY_RELEASE = "https://github.com/XTLS/Xray-core/releases/latest/download"
XRAY_MAX_BYTES = 80 * 1024 * 1024
SKIP_PROTOCOLS = {"freedom", "blackhole", "dns", "loopback", "direct", "block"}
TRANSPORTS = {"tcp", "ws", "grpc", "httpupgrade", "xhttp"}
WATCH_INTERVAL = 20


class ParseError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def make_entry(kind: str, label: str, **data) -> dict:
    return {"id": secrets.token_hex(4), "type": kind, "label": label[:80], **data}


def parts_of(line: str):
    try:
        parts = urlsplit(line)
        return parts, parts.hostname, parts.port
    except ValueError:
        raise ParseError("bad_link")


def parse_http(parts, host, port) -> dict:
    if not host or not port:
        raise ParseError("bad_link")
    return make_entry("http", unquote(parts.fragment) or f"{host}:{port}", url=f"http://{parts.netloc}")


def parse_socks(parts, host, port) -> dict:
    if not host or not port:
        raise ParseError("bad_link")
    server = {"address": host, "port": port}
    if parts.username:
        server["users"] = [{"user": unquote(parts.username), "pass": unquote(parts.password or "")}]
    outbound = {"protocol": "socks", "settings": {"servers": [server]}}
    return make_entry("socks5", unquote(parts.fragment) or f"{host}:{port}", outbound=outbound)


def parse_vless(parts, host, port) -> dict:
    if not host or not port or not parts.username:
        raise ParseError("bad_link")
    try:
        user_id = str(uuid.UUID(unquote(parts.username)))
    except ValueError:
        raise ParseError("bad_uuid")
    q = {k: v[0] for k, v in parse_qs(parts.query, keep_blank_values=True).items()}
    network = {"raw": "tcp"}.get(q.get("type", "tcp"), q.get("type", "tcp"))
    if network not in TRANSPORTS:
        raise ParseError("unsupported_transport")
    security = q.get("security", "none")
    if security not in ("none", "tls", "reality"):
        raise ParseError("unsupported_security")

    user = {"id": user_id, "encryption": q.get("encryption", "none")}
    if q.get("flow"):
        user["flow"] = q["flow"]

    stream = {"network": network, "security": security}
    if network == "ws":
        stream["wsSettings"] = {"path": q.get("path", "/"), "headers": {"Host": q["host"]} if q.get("host") else {}}
    elif network == "grpc":
        grpc = {"serviceName": q.get("serviceName", ""), "multiMode": q.get("mode") == "multi"}
        if q.get("authority"):
            grpc["authority"] = q["authority"]
        stream["grpcSettings"] = grpc
    elif network == "httpupgrade":
        stream["httpupgradeSettings"] = {"path": q.get("path", "/"), "host": q.get("host", "")}
    elif network == "xhttp":
        stream["xhttpSettings"] = {"path": q.get("path", "/"), "host": q.get("host", ""), "mode": q.get("mode", "auto")}

    if security == "tls":
        tls = {k: v for k, v in (("serverName", q.get("sni")), ("fingerprint", q.get("fp"))) if v}
        if q.get("alpn"):
            tls["alpn"] = q["alpn"].split(",")
        if q.get("allowInsecure") in ("1", "true"):
            tls["allowInsecure"] = True
        stream["tlsSettings"] = tls
    elif security == "reality":
        if not q.get("pbk"):
            raise ParseError("bad_reality")
        stream["realitySettings"] = {
            "serverName": q.get("sni", ""),
            "fingerprint": q.get("fp") or "chrome",
            "publicKey": q["pbk"],
            "shortId": q.get("sid", ""),
            "spiderX": q.get("spx", ""),
        }

    outbound = {
        "protocol": "vless",
        "settings": {"vnext": [{"address": host, "port": port, "users": [user]}]},
        "streamSettings": stream,
    }
    return make_entry("vless", unquote(parts.fragment) or f"{host}:{port}", outbound=outbound)


def parse_link(line: str) -> dict:
    line = line.strip()
    if len(line) > MAX_LINE:
        raise ParseError("too_long")
    parts, host, port = parts_of(line)
    scheme = parts.scheme.lower()
    if scheme == "http":
        return parse_http(parts, host, port)
    if scheme in ("socks5", "socks5h"):
        return parse_socks(parts, host, port)
    if scheme == "vless":
        return parse_vless(parts, host, port)
    raise ParseError("unsupported")


def describe(outbound: dict) -> str:
    settings = outbound.get("settings") or {}
    for key in ("vnext", "servers"):
        items = settings.get(key)
        if isinstance(items, list) and items and isinstance(items[0], dict):
            address, port = items[0].get("address"), items[0].get("port")
            if address:
                return f"{address}:{port}" if port else str(address)
    return str(outbound.get("protocol", "proxy"))


def parse_config(obj) -> dict:
    if not isinstance(obj, dict):
        raise ParseError("bad_config")
    outbound = None
    if isinstance(obj.get("outbounds"), list):
        candidates = [o for o in obj["outbounds"] if isinstance(o, dict) and o.get("protocol") and o["protocol"] not in SKIP_PROTOCOLS]
        outbound = next((o for o in candidates if o.get("tag") == "proxy"), candidates[0] if candidates else None)
    elif obj.get("protocol") and obj["protocol"] not in SKIP_PROTOCOLS:
        outbound = obj
    if outbound is None:
        raise ParseError("no_outbound")
    label = obj.get("remarks") if isinstance(obj.get("remarks"), str) and obj["remarks"].strip() else describe(outbound)
    return make_entry("xray", label.strip(), outbound=outbound, protocol=str(outbound["protocol"]))


def parse_text(text: str) -> tuple[list[dict], list[dict]]:
    text = (text or "").strip().lstrip("\ufeff")
    entries, errors = [], []
    if not text:
        return entries, [{"code": "empty", "n": 0}]
    if text[0] in "{[":
        decoder, pos, count = json.JSONDecoder(), 0, 0
        while pos < len(text):
            while pos < len(text) and (text[pos].isspace() or text[pos] == ","):
                pos += 1
            if pos >= len(text):
                break
            try:
                obj, pos = decoder.raw_decode(text, pos)
            except ValueError:
                errors.append({"code": "bad_json", "n": count + 1})
                break
            for item in obj if isinstance(obj, list) else [obj]:
                count += 1
                try:
                    entries.append(parse_config(item))
                except ParseError as e:
                    errors.append({"code": e.code, "n": count})
    else:
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        for n, line in enumerate(lines, 1):
            try:
                entries.append(parse_link(line))
            except ParseError as e:
                errors.append({"code": e.code, "n": n})
    return entries, errors


def build_xray_config(outbound: dict, port: int) -> dict:
    out = copy.deepcopy(outbound)
    out["tag"] = "proxy"
    out.pop("sendThrough", None)
    out.setdefault("streamSettings", {}).setdefault("sockopt", {}).setdefault("domainStrategy", "UseIPv4")
    return {
        "log": {"loglevel": "warning"},
        "dns": {"servers": ["1.1.1.1", "8.8.8.8"], "queryStrategy": "UseIPv4"},
        "inbounds": [{"tag": "http", "listen": "127.0.0.1", "port": port, "protocol": "http", "settings": {}}],
        "outbounds": [out, {"tag": "direct", "protocol": "freedom"}],
        "routing": {"domainStrategy": "AsIs", "rules": [{"type": "field", "inboundTag": ["http"], "outboundTag": "proxy"}]},
    }


def asset_name() -> str | None:
    arch = {
        "x86_64": "64", "amd64": "64", "aarch64": "arm64-v8a", "arm64": "arm64-v8a",
        "armv8l": "arm32-v7a", "armv7l": "arm32-v7a", "i686": "32", "i386": "32",
    }.get(platform.machine().lower())
    if not arch:
        return None
    system = "android" if os.environ.get("TERMUX_VERSION") and arch == "arm64-v8a" else "linux"
    return f"Xray-{system}-{arch}.zip"


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


async def download(url: str, limit: int) -> bytes:
    timeout = aiohttp.ClientTimeout(total=300, connect=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status}")
            buf = bytearray()
            async for chunk in resp.content.iter_chunked(262144):
                buf.extend(chunk)
                if len(buf) > limit:
                    raise RuntimeError("file too large")
            return bytes(buf)


async def probe(url: str) -> tuple[bool, int, str]:
    started = time.monotonic()
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            async with session.get(PROBE_URL, proxy=url) as resp:
                if resp.status == 200:
                    return True, int((time.monotonic() - started) * 1000), ""
                return False, 0, f"HTTP {resp.status}"
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        return False, 0, type(e).__name__


class Xray:
    def __init__(self):
        self.proc: asyncio.subprocess.Process | None = None
        self.log = XRAY_DIR / "xray.log"
        self.pidfile = XRAY_DIR / "xray.pid"
        self.cleanup_stale()

    def cleanup_stale(self):
        try:
            pid = int(self.pidfile.read_text().strip())
            if b"xray" in open(f"/proc/{pid}/cmdline", "rb").read():
                os.kill(pid, signal.SIGTERM)
        except (OSError, ValueError):
            pass

    def alive(self) -> bool:
        return self.proc is not None and self.proc.returncode is None

    def tail(self) -> str:
        try:
            return self.log.read_text(errors="replace").strip()[-300:]
        except OSError:
            return ""

    async def start(self, binary: str, outbound: dict) -> tuple[str | None, str]:
        await self.stop()
        ensure_dirs()
        XRAY_DIR.mkdir(parents=True, exist_ok=True)
        port = free_port()
        config = XRAY_DIR / "config.json"
        write_json(config, build_xray_config(outbound, port))
        with open(self.log, "wb") as log:
            try:
                self.proc = await asyncio.create_subprocess_exec(binary, "run", "-c", str(config), stdout=log, stderr=asyncio.subprocess.STDOUT)
            except OSError as e:
                return None, str(e)
        try:
            self.pidfile.write_text(str(self.proc.pid))
        except OSError:
            pass
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.proc.returncode is not None:
                return None, self.tail() or f"exit {self.proc.returncode}"
            try:
                _, writer = await asyncio.open_connection("127.0.0.1", port)
                writer.close()
                return f"http://127.0.0.1:{port}", ""
            except OSError:
                await asyncio.sleep(0.2)
        await self.stop()
        return None, "start timeout"

    async def stop(self):
        proc, self.proc = self.proc, None
        if proc and proc.returncode is None:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), 5)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
        try:
            self.pidfile.unlink()
        except OSError:
            pass


class ProxyPool:
    def __init__(self, fernet: Fernet):
        self.fernet = fernet
        self.entries: list[dict] = self.load()
        self.index = 0
        self.active = ""
        self.url: str | None = None
        self.status: dict[str, dict] = {}
        self.binary = {"state": "", "detail": ""}
        self.xray = Xray()

    def load(self) -> list[dict]:
        try:
            data = json.loads(self.fernet.decrypt(PROXIES_FILE.read_bytes()))
        except (OSError, InvalidToken, ValueError):
            return []
        return [e for e in data if isinstance(e, dict) and e.get("id")] if isinstance(data, list) else []

    def save(self):
        payload = json.dumps(self.entries, ensure_ascii=False).encode("utf-8")
        write_bytes_atomic(PROXIES_FILE, self.fernet.encrypt(payload))

    def add(self, entries: list[dict]) -> int:
        room = max(0, MAX_PROXIES - len(self.entries))
        taken = entries[:room]
        self.entries.extend(taken)
        if taken:
            self.save()
        return len(taken)

    def remove(self, entry_id: str) -> bool:
        kept = [e for e in self.entries if e["id"] != entry_id]
        if len(kept) == len(self.entries):
            return False
        self.entries = kept
        self.status.pop(entry_id, None)
        if self.active == entry_id:
            self.active, self.url = "", None
        self.index = 0
        self.save()
        return True

    def view(self) -> dict:
        rows = []
        for entry in self.entries:
            kind = entry["type"]
            if kind == "xray":
                kind = entry.get("protocol", "xray")
            rows.append({
                "id": entry["id"], "type": kind, "label": entry["label"],
                "active": entry["id"] == self.active, "status": self.status.get(entry["id"]),
            })
        return {"entries": rows, "max": MAX_PROXIES, "binary": self.binary}

    def binary_path(self) -> str | None:
        for candidate in (os.environ.get("MRBEAST_XRAY"), shutil.which("xray"), str(BIN_DIR / "xray")):
            if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
        return None

    async def ensure_binary(self) -> str | None:
        path = self.binary_path()
        if path:
            return path
        name = asset_name()
        if not name:
            self.binary = {"state": "error", "detail": "unsupported platform"}
            return None
        self.binary = {"state": "downloading", "detail": name}
        try:
            archive = await download(f"{XRAY_RELEASE}/{name}", XRAY_MAX_BYTES)
            digest = (await download(f"{XRAY_RELEASE}/{name}.dgst", 8192)).decode(errors="replace")
            match = re.search(r"SHA2-256=\s*([0-9a-fA-F]{64})", digest)
            if not match or hashlib.sha256(archive).hexdigest() != match.group(1).lower():
                raise RuntimeError("checksum mismatch")
            BIN_DIR.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(archive)) as zf:
                write_bytes_atomic(BIN_DIR / "xray", zf.read("xray"))
            os.chmod(BIN_DIR / "xray", 0o755)
            proc = await asyncio.create_subprocess_exec(str(BIN_DIR / "xray"), "version", stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
            if await proc.wait() != 0:
                raise RuntimeError("downloaded binary does not run")
        except Exception as e:
            logger.error(f"Xray download failed: {e}")
            self.binary = {"state": "error", "detail": str(e)[:200]}
            return None
        self.binary = {"state": "ready", "detail": ""}
        return str(BIN_DIR / "xray")

    def record(self, entry_id: str, ok: bool, ms: int = 0, error: str = ""):
        self.status[entry_id] = {"ok": ok, "ms": ms, "error": error}

    async def open_entry(self, entry: dict) -> str | None:
        if entry["type"] == "http":
            await self.xray.stop()
            return entry["url"]
        binary = await self.ensure_binary()
        if not binary:
            self.record(entry["id"], False, 0, "xray")
            return None
        url, error = await self.xray.start(binary, entry["outbound"])
        if url is None:
            logger.error(f"Xray start failed for {entry['label']}: {error}")
            self.record(entry["id"], False, 0, error[:120])
        return url

    async def connect(self, stop: asyncio.Event) -> str | None:
        count = len(self.entries)
        for step in range(count):
            if stop.is_set():
                return None
            position = (self.index + step) % count
            entry = self.entries[position]
            url = await self.open_entry(entry)
            if url:
                ok, ms, error = await probe(url)
                self.record(entry["id"], ok, ms, error)
                if ok:
                    self.index, self.active, self.url = position, entry["id"], url
                    logger.info(f"Using proxy {entry['label']} ({ms} ms)")
                    return url
        await self.xray.stop()
        self.active, self.url = "", None
        return None

    async def watch(self):
        misses = 0
        while True:
            await asyncio.sleep(WATCH_INTERVAL)
            if self.entries and self.entries[self.index % len(self.entries)]["type"] != "http" and not self.xray.alive():
                return
            ok, ms, error = await probe(self.url)
            self.record(self.active, ok, ms, error)
            misses = 0 if ok else misses + 1
            if misses >= 2:
                return

    async def advance(self):
        if self.entries:
            self.index = (self.index + 1) % len(self.entries)
        self.active, self.url = "", None
        await self.xray.stop()

    async def stop(self):
        self.active, self.url = "", None
        await self.xray.stop()
