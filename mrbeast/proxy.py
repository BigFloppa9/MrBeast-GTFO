import asyncio
import base64
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
PROBE_TIMEOUT = 8
SLOW_MS = 1000
RECHECK_INTERVAL = 300
MAINTAIN_INTERVAL = 600
DOWN_LIMIT = 86400
PENALTY_SECONDS = 180
SUB_UA = "Happ/2.0.0"
SUB_MAX_BYTES = 2 * 1024 * 1024


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


def prepare_outbound(outbound: dict, tag: str) -> dict:
    out = copy.deepcopy(outbound)
    out["tag"] = tag
    out.pop("sendThrough", None)
    out.setdefault("streamSettings", {}).setdefault("sockopt", {}).setdefault("domainStrategy", "UseIPv4")
    return out


def base_config(inbounds: list, outbounds: list, rules: list) -> dict:
    return {
        "log": {"loglevel": "warning"},
        "dns": {"servers": ["1.1.1.1", "8.8.8.8"], "queryStrategy": "UseIPv4"},
        "inbounds": inbounds,
        "outbounds": outbounds + [{"tag": "direct", "protocol": "freedom"}],
        "routing": {"domainStrategy": "AsIs", "rules": rules},
    }


def http_inbound(tag: str, port: int) -> dict:
    return {"tag": tag, "listen": "127.0.0.1", "port": port, "protocol": "http", "settings": {}}


def build_xray_config(outbound: dict, port: int) -> dict:
    return base_config(
        [http_inbound("http", port)], [prepare_outbound(outbound, "proxy")],
        [{"type": "field", "inboundTag": ["http"], "outboundTag": "proxy"}],
    )


def build_multi_config(entries: list[dict]) -> tuple[dict, dict]:
    ports = dict(zip((e["id"] for e in entries), free_ports(len(entries))))
    inbounds, outbounds, rules = [], [], []
    for i, entry in enumerate(entries):
        inbounds.append(http_inbound(f"i{i}", ports[entry["id"]]))
        outbounds.append(prepare_outbound(entry["outbound"], f"o{i}"))
        rules.append({"type": "field", "inboundTag": [f"i{i}"], "outboundTag": f"o{i}"})
    return base_config(inbounds, outbounds, rules), ports


def decode_subscription(body: str) -> str:
    text = (body or "").strip().lstrip("\ufeff")
    if not text or text[0] in "{[" or "://" in text.splitlines()[0]:
        return text
    compact = re.sub(r"\s+", "", text).replace("-", "+").replace("_", "/")
    try:
        raw = base64.b64decode(compact + "=" * (-len(compact) % 4)).decode("utf-8", errors="ignore").strip()
    except ValueError:
        return text
    return raw if raw and (raw[0] in "{[" or "://" in raw) else text


def parse_subscription(body: str) -> tuple[list[dict], int]:
    entries, errors = parse_text(decode_subscription(body))
    return entries, len([e for e in errors if e["code"] != "empty"])


async def fetch_subscription(url: str, via: str | None = None) -> str:
    last = "failed"
    for proxy in ((None, via) if via else (None,)):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=25), headers={"User-Agent": SUB_UA}) as session:
                async with session.get(url, proxy=proxy) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"HTTP {resp.status}")
                    data = await resp.content.read(SUB_MAX_BYTES + 1)
                    if len(data) > SUB_MAX_BYTES:
                        raise RuntimeError("too large")
                    return data.decode("utf-8", errors="replace")
        except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as e:
            last = str(e) or type(e).__name__
    raise RuntimeError(last[:160])


def asset_name() -> str | None:
    arch = {
        "x86_64": "64", "amd64": "64", "aarch64": "arm64-v8a", "arm64": "arm64-v8a",
        "armv8l": "arm32-v7a", "armv7l": "arm32-v7a", "i686": "32", "i386": "32",
    }.get(platform.machine().lower())
    if not arch:
        return None
    system = "android" if os.environ.get("TERMUX_VERSION") and arch == "arm64-v8a" else "linux"
    return f"Xray-{system}-{arch}.zip"


def free_ports(count: int) -> list[int]:
    socks = [socket.socket() for _ in range(count)]
    try:
        for sock in socks:
            sock.bind(("127.0.0.1", 0))
        return [sock.getsockname()[1] for sock in socks]
    finally:
        for sock in socks:
            sock.close()


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


async def probe(url: str, timeout: int = 15) -> tuple[bool, int, str]:
    started = time.monotonic()
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(PROBE_URL, proxy=url) as resp:
                if resp.status == 200:
                    return True, max(1, int((time.monotonic() - started) * 1000)), ""
                return False, 0, f"HTTP {resp.status}"
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        return False, 0, type(e).__name__


class Xray:
    def __init__(self, name: str = "main"):
        self.proc: asyncio.subprocess.Process | None = None
        self.config = XRAY_DIR / f"{name}.json"
        self.log = XRAY_DIR / f"{name}.log"
        self.pidfile = XRAY_DIR / f"{name}.pid"
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

    async def start(self, binary: str, conf: dict, port: int) -> str:
        await self.stop()
        ensure_dirs()
        XRAY_DIR.mkdir(parents=True, exist_ok=True)
        write_json(self.config, conf)
        with open(self.log, "wb") as log:
            try:
                self.proc = await asyncio.create_subprocess_exec(binary, "run", "-c", str(self.config), stdout=log, stderr=asyncio.subprocess.STDOUT)
            except OSError as e:
                return str(e)
        try:
            self.pidfile.write_text(str(self.proc.pid))
        except OSError:
            pass
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.proc.returncode is not None:
                return self.tail() or f"exit {self.proc.returncode}"
            try:
                _, writer = await asyncio.open_connection("127.0.0.1", port)
                writer.close()
                return ""
            except OSError:
                await asyncio.sleep(0.2)
        await self.stop()
        return "start timeout"

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
        self.entries, self.subs = self.load()
        self.active = ""
        self.url: str | None = None
        self.status: dict[str, dict] = {}
        self.binary = {"state": "", "detail": ""}
        self.xray = Xray("main")
        self.prober = Xray("probe")
        self.probe_lock = asyncio.Lock()
        self.dirty = False
        self.last_full = 0.0
        self.penalty: dict[str, float] = {}

    def load(self) -> tuple[list[dict], list[dict]]:
        try:
            data = json.loads(self.fernet.decrypt(PROXIES_FILE.read_bytes()))
        except (OSError, InvalidToken, ValueError):
            return [], []
        if isinstance(data, list):
            data = {"entries": data, "subs": []}
        if not isinstance(data, dict):
            return [], []
        entries = [e for e in data.get("entries", []) if isinstance(e, dict) and e.get("id")]
        subs = [s for s in data.get("subs", []) if isinstance(s, dict) and s.get("id")]
        return entries, subs

    def save(self):
        payload = json.dumps({"entries": self.entries, "subs": self.subs}, ensure_ascii=False).encode("utf-8")
        write_bytes_atomic(PROXIES_FILE, self.fernet.encrypt(payload))
        self.dirty = False

    def flush(self):
        if self.dirty:
            self.save()

    def add(self, entries: list[dict]) -> int:
        taken = entries[:max(0, MAX_PROXIES - len(self.entries))]
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
        self.save()
        return True

    def set_subscription(self, url: str, entries: list[dict], sub_id: str | None = None) -> dict:
        sub = next((s for s in self.subs if s["id"] == sub_id), None)
        if sub is None:
            sub = {"id": secrets.token_hex(4), "url": url, "label": (urlsplit(url).hostname or url)[:60]}
            self.subs.append(sub)
        self.entries = [e for e in self.entries if e.get("sub") != sub["id"]]
        room = max(0, MAX_PROXIES - len(self.entries))
        for entry in entries[:room]:
            entry["sub"] = sub["id"]
            self.entries.append(entry)
        sub["count"] = min(len(entries), room)
        sub["updated"] = int(time.time())
        self.save()
        return sub

    def remove_subscription(self, sub_id: str) -> bool:
        kept = [s for s in self.subs if s["id"] != sub_id]
        if len(kept) == len(self.subs):
            return False
        self.subs = kept
        self.entries = [e for e in self.entries if e.get("sub") != sub_id]
        if self.active and not any(e["id"] == self.active for e in self.entries):
            self.active, self.url = "", None
        self.save()
        return True

    def view(self) -> dict:
        rows = []
        for entry in self.entries:
            kind = entry.get("protocol", "xray") if entry["type"] == "xray" else entry["type"]
            rows.append({
                "id": entry["id"], "type": kind, "label": entry["label"], "sub": entry.get("sub", ""),
                "active": entry["id"] == self.active, "status": self.status.get(entry["id"]),
            })
        subs = [{"id": s["id"], "label": s["label"], "count": s.get("count", 0), "updated": s.get("updated", 0)} for s in self.subs]
        return {"entries": rows, "subs": subs, "max": MAX_PROXIES, "binary": self.binary}

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
        entry = next((e for e in self.entries if e["id"] == entry_id), None)
        if entry is None:
            return
        self.status[entry_id] = {"ok": ok, "ms": ms, "error": error}
        if ok and "down_since" in entry:
            del entry["down_since"]
            self.dirty = True
        elif not ok and "down_since" not in entry:
            entry["down_since"] = int(time.time())
            self.dirty = True

    def cleanup(self) -> int:
        limit = time.time() - DOWN_LIMIT
        keep = [e for e in self.entries if e["id"] == self.active or e.get("down_since", time.time()) > limit]
        removed = len(self.entries) - len(keep)
        if removed:
            self.entries = keep
            self.dirty = True
        return removed

    async def probe_group(self, entries: list[dict]) -> dict:
        binary = await self.ensure_binary()
        if not binary:
            return {e["id"]: (False, 0, "xray") for e in entries}
        conf, ports = build_multi_config(entries)
        error = await self.prober.start(binary, conf, next(iter(ports.values())))
        if error:
            await self.prober.stop()
            if len(entries) == 1:
                return {entries[0]["id"]: (False, 0, error[:120])}
            merged = {}
            for entry in entries:
                merged.update(await self.probe_group([entry]))
            return merged
        try:
            gate = asyncio.Semaphore(20)

            async def one(entry):
                async with gate:
                    return entry["id"], await probe(f"http://127.0.0.1:{ports[entry['id']]}", PROBE_TIMEOUT)

            return dict(await asyncio.gather(*(one(e) for e in entries)))
        finally:
            await self.prober.stop()

    async def probe_all(self) -> dict:
        async with self.probe_lock:
            results: dict = {}
            gate = asyncio.Semaphore(20)

            async def direct(entry):
                async with gate:
                    results[entry["id"]] = await probe(entry["url"], PROBE_TIMEOUT)

            plain = [e for e in self.entries if e["type"] == "http"]
            other = [e for e in self.entries if e["type"] != "http"]

            async def grouped():
                if other:
                    results.update(await self.probe_group(other))

            await asyncio.gather(grouped(), *(direct(e) for e in plain))
            for entry_id, (ok, ms, error) in results.items():
                self.record(entry_id, ok, ms, error)
            self.flush()
            return results

    async def open_entry(self, entry: dict) -> str | None:
        if entry["type"] == "http":
            await self.xray.stop()
            return entry["url"]
        binary = await self.ensure_binary()
        if not binary:
            self.record(entry["id"], False, 0, "xray")
            return None
        port = free_ports(1)[0]
        error = await self.xray.start(binary, build_xray_config(entry["outbound"], port), port)
        if error:
            logger.error(f"Xray start failed for {entry['label']}: {error}")
            self.record(entry["id"], False, 0, error[:120])
            return None
        return f"http://127.0.0.1:{port}"

    async def connect(self, stop: asyncio.Event) -> str | None:
        results = await self.probe_all()
        now = time.monotonic()
        ranked = sorted(
            (e for e in self.entries if results.get(e["id"], (False,))[0]),
            key=lambda e: (self.penalty.get(e["id"], 0) > now, results[e["id"]][1]),
        )
        for entry in ranked:
            if stop.is_set():
                return None
            url = await self.open_entry(entry)
            if url:
                ok, ms, error = await probe(url)
                self.record(entry["id"], ok, ms, error)
                if ok:
                    self.active, self.url, self.last_full = entry["id"], url, time.monotonic()
                    self.flush()
                    logger.info(f"Using proxy {entry['label']} ({ms} ms)")
                    return url
        await self.xray.stop()
        self.active, self.url = "", None
        self.flush()
        return None

    async def watch(self):
        misses = 0
        while True:
            await asyncio.sleep(WATCH_INTERVAL)
            active = next((e for e in self.entries if e["id"] == self.active), None)
            if active is None:
                return
            if active["type"] != "http" and not self.xray.alive():
                self.record(self.active, False, 0, "xray stopped")
                return
            ok, ms, error = await probe(self.url)
            self.record(self.active, ok, ms, error)
            if not ok:
                misses += 1
                if misses >= 2:
                    return
                continue
            misses = 0
            if ms > SLOW_MS and time.monotonic() - self.last_full > RECHECK_INTERVAL:
                results = await self.probe_all()
                self.last_full = time.monotonic()
                better = [(r[1], i) for i, r in results.items() if r[0] and i != self.active]
                if better and min(better)[0] < ms:
                    return

    def penalize(self):
        if self.active:
            self.penalty[self.active] = time.monotonic() + PENALTY_SECONDS

    async def release(self):
        self.active, self.url = "", None
        await self.xray.stop()

    async def maintain(self, stop: asyncio.Event):
        while True:
            try:
                await asyncio.wait_for(stop.wait(), MAINTAIN_INTERVAL)
                return
            except asyncio.TimeoutError:
                pass
            if self.entries:
                await self.probe_all()
                if self.cleanup():
                    self.flush()

    async def stop(self):
        await self.release()
        await self.prober.stop()
