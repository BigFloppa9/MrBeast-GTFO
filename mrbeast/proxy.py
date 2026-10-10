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
from urllib.parse import parse_qs, quote, unquote, urlsplit

import aiohttp

from . import happ_crypt
from cryptography.fernet import Fernet, InvalidToken

from .config import BIN_DIR, PROXIES_FILE, XRAY_DIR, ensure_dirs, write_bytes_atomic, write_json

logger = logging.getLogger("mrbeast.proxy")

MAX_PROXIES = 1000
MAX_LINE = 8000
PROBE_URL = "https://discord.com/api/v10/gateway"
XRAY_RELEASE = "https://github.com/XTLS/Xray-core/releases/latest/download"
XRAY_MAX_BYTES = 80 * 1024 * 1024
SKIP_PROTOCOLS = {"freedom", "blackhole", "dns", "loopback", "direct", "block"}
TRANSPORTS = {"tcp", "ws", "grpc", "httpupgrade", "xhttp"}
WATCH_INTERVAL = 20
PROBE_TIMEOUT = 8
SLOW_MS = 3000
PROBE_CHUNK = 60
RECHECK_INTERVAL = 300
MAINTAIN_INTERVAL = 600
DOWN_LIMIT = 86400
PENALTY_SECONDS = 180
SUB_AGENTS = (
    "Happ/2.0.0",
    "v2rayN/7.8.2",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "curl/8.5.0",
)
SUB_MAX_BYTES = 4 * 1024 * 1024
SUB_TIMEOUT = 15
RECOVER_INTERVAL = 90
FIRST_CHECK_DELAY = 45
CHECK_GAP_CAP = 1800
NET_PROBES = (("1.1.1.1", 443), ("8.8.8.8", 443), ("9.9.9.9", 443), ("77.88.8.8", 443))
WRAP_SCHEMES = {"happ", "v2raytun", "hiddify", "incy", "sub", "clash", "clashmeta", "sing-box", "v2rayng", "v2rayn", "karing", "flclash", "stash", "shadowrocket", "streisand", "nekobox", "husi", "singbox"}


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


def query_of(parts) -> dict:
    return {k: v[0] for k, v in parse_qs(parts.query, keep_blank_values=True).items()}


def build_stream(q: dict, default_security: str = "none") -> dict:
    network = {"raw": "tcp", "splithttp": "xhttp", "h2": "http"}.get(q.get("type", "tcp"), q.get("type", "tcp"))
    if network not in TRANSPORTS:
        raise ParseError("unsupported_transport")
    security = q.get("security") or default_security or "none"
    if security not in ("none", "tls", "reality"):
        raise ParseError("unsupported_security")

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
        xhttp = {"path": q.get("path", "/"), "host": q.get("host", ""), "mode": q.get("mode", "auto")}
        if q.get("extra"):
            try:
                extra = json.loads(q["extra"])
            except ValueError:
                extra = None
            if isinstance(extra, dict):
                xhttp["extra"] = extra
        stream["xhttpSettings"] = xhttp

    if security == "tls":
        tls = {k: v for k, v in (("serverName", q.get("sni") or q.get("peer")), ("fingerprint", q.get("fp"))) if v}
        if q.get("alpn"):
            tls["alpn"] = [a for a in q["alpn"].split(",") if a]
        if q.get("allowInsecure") in ("1", "true") or q.get("insecure") in ("1", "true"):
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
    return stream


def label_of(parts, host, port) -> str:
    return unquote(parts.fragment).strip() or f"{host}:{port}"


def parse_vless(parts, host, port) -> dict:
    if not host or not port or not parts.username:
        raise ParseError("bad_link")
    try:
        user_id = str(uuid.UUID(unquote(parts.username)))
    except ValueError:
        raise ParseError("bad_uuid")
    q = query_of(parts)
    user = {"id": user_id, "encryption": q.get("encryption", "none")}
    if q.get("flow"):
        user["flow"] = q["flow"]
    outbound = {
        "protocol": "vless",
        "settings": {"vnext": [{"address": host, "port": port, "users": [user]}]},
        "streamSettings": build_stream(q),
    }
    return make_entry("vless", label_of(parts, host, port), outbound=outbound)


def b64_text(raw: str) -> str:
    compact = re.sub(r"\s+", "", raw).replace("-", "+").replace("_", "/")
    try:
        return base64.b64decode(compact + "=" * (-len(compact) % 4)).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        raise ParseError("bad_link")


def parse_vmess(line: str) -> dict:
    try:
        data = json.loads(b64_text(line.split("://", 1)[1].split("#", 1)[0]))
    except ValueError:
        raise ParseError("bad_link")
    if not isinstance(data, dict) or not data.get("add") or not data.get("id"):
        raise ParseError("bad_link")
    try:
        port, user_id = int(data.get("port")), str(uuid.UUID(str(data["id"])))
        alter = int(data.get("aid") or 0)
    except (TypeError, ValueError):
        raise ParseError("bad_link")
    q = {
        "type": str(data.get("net") or "tcp"), "path": str(data.get("path") or "/"), "host": str(data.get("host") or ""),
        "security": "tls" if str(data.get("tls") or "").lower() == "tls" else "none",
        "sni": str(data.get("sni") or ""), "alpn": str(data.get("alpn") or ""), "fp": str(data.get("fp") or ""),
        "serviceName": str(data.get("path") or ""), "mode": "multi" if data.get("type") == "multi" else "gun",
    }
    outbound = {
        "protocol": "vmess",
        "settings": {"vnext": [{"address": str(data["add"]), "port": port, "users": [{"id": user_id, "alterId": alter, "security": str(data.get("scy") or "auto")}]}]},
        "streamSettings": build_stream(q),
    }
    return make_entry("vmess", str(data.get("ps") or f"{data['add']}:{port}"), outbound=outbound)


def parse_trojan(parts, host, port) -> dict:
    if not host or not port or not parts.username:
        raise ParseError("bad_link")
    q = query_of(parts)
    outbound = {
        "protocol": "trojan",
        "settings": {"servers": [{"address": host, "port": port, "password": unquote(parts.username)}]},
        "streamSettings": build_stream(q, "tls"),
    }
    return make_entry("trojan", label_of(parts, host, port), outbound=outbound)


def parse_ss(line: str) -> dict:
    body, _, fragment = line.split("://", 1)[1].partition("#")
    body, _, query = body.partition("?")
    if "plugin=" in query:
        raise ParseError("unsupported_plugin")
    if "@" not in body:
        body = b64_text(body)
    userinfo, _, hostport = body.rpartition("@")
    if not userinfo or ":" not in hostport:
        raise ParseError("bad_link")
    if ":" not in userinfo:
        userinfo = b64_text(userinfo)
    method, _, password = unquote(userinfo).partition(":")
    host, _, port_text = hostport.rpartition(":")
    try:
        port = int(port_text)
    except ValueError:
        raise ParseError("bad_link")
    if not method or not host:
        raise ParseError("bad_link")
    outbound = {"protocol": "shadowsocks", "settings": {"servers": [{"address": host.strip("[]"), "port": port, "method": method, "password": password}]}}
    return make_entry("shadowsocks", unquote(fragment).strip() or f"{host}:{port}", outbound=outbound)


def unwrap_link(line: str) -> str:
    low = line.lower()
    crypt = re.match(r"happ://(crypt\d*)/", line, re.I)
    if crypt:
        if crypt.group(1).lower() == "crypt5":
            return line
        raise ParseError("crypt_unsupported")
    if "happ%3a%2f%2fcrypt" in low:
        raise ParseError("crypt_unsupported")
    scheme = low.split("://", 1)[0] if "://" in low else ""
    tg = urlsplit(line) if scheme in ("tg", "http", "https") else None
    if tg is not None and (scheme == "tg" or (tg.hostname or "").lower() in ("t.me", "telegram.me")):
        kind = tg.netloc if scheme == "tg" else tg.path.strip("/")
        q = {k: v[0] for k, v in parse_qs(tg.query).items()}
        if kind == "socks" and q.get("server") and q.get("port"):
            auth = f"{quote(q.get('user', ''), safe='')}:{quote(q.get('pass', ''), safe='')}@" if q.get("user") else ""
            return f"socks5://{auth}{q['server']}:{q['port']}"
        if kind in ("proxy", "mtproto", "socks"):
            raise ParseError("mtproto_unsupported")
    if scheme in WRAP_SCHEMES:
        rest = unquote(line.split("://", 1)[1])
        found = re.search(r"https?://[^\s]+", rest)
        if found:
            return found.group(0)
        raise ParseError("bad_link")
    return line


def is_sub_url(line: str) -> bool:
    if line.lower().startswith("happ://crypt5/"):
        return True
    try:
        parts = urlsplit(line)
    except ValueError:
        return False
    if parts.scheme.lower() not in ("http", "https") or not parts.hostname:
        return False
    return parts.scheme.lower() == "https" or parts.path not in ("", "/") or bool(parts.query)


def parse_link(line: str) -> dict:
    line = line.strip()
    if len(line) > MAX_LINE:
        raise ParseError("too_long")
    low = line.lower()
    if low.startswith("vmess://"):
        return parse_vmess(line)
    if low.startswith("ss://"):
        return parse_ss(line)
    parts, host, port = parts_of(line)
    scheme = parts.scheme.lower()
    if scheme == "http":
        return parse_http(parts, host, port)
    if scheme in ("socks5", "socks5h", "socks"):
        return parse_socks(parts, host, port)
    if scheme == "vless":
        return parse_vless(parts, host, port)
    if scheme == "trojan":
        return parse_trojan(parts, host, port)
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


FORM_KINDS = ("socks5", "http", "vless", "vmess", "trojan", "shadowsocks", "xray")
STREAM_KINDS = ("vless", "vmess", "trojan")
SS_METHODS = (
    "aes-128-gcm", "aes-256-gcm", "chacha20-ietf-poly1305", "xchacha20-ietf-poly1305",
    "2022-blake3-aes-128-gcm", "2022-blake3-aes-256-gcm", "2022-blake3-chacha20-poly1305",
)


def text_field(fields: dict, key: str, limit: int = 300) -> str:
    value = fields.get(key)
    if value is None:
        return ""
    value = str(value).strip()
    if len(value) > limit:
        raise ParseError("too_long")
    return value


def port_field(fields: dict) -> int:
    try:
        port = int(str(fields.get("port") or "").strip())
    except ValueError:
        raise ParseError("bad_port")
    if not 1 <= port <= 65535:
        raise ParseError("bad_port")
    return port


def stream_query(fields: dict) -> dict:
    q = {
        "type": text_field(fields, "network") or "tcp",
        "security": text_field(fields, "security"),
        "sni": text_field(fields, "sni"),
        "fp": text_field(fields, "fp"),
        "alpn": text_field(fields, "alpn"),
        "pbk": text_field(fields, "pbk"),
        "sid": text_field(fields, "sid"),
        "spx": text_field(fields, "spx"),
        "path": text_field(fields, "path") or "/",
        "host": text_field(fields, "host_header"),
        "serviceName": text_field(fields, "service"),
        "mode": text_field(fields, "mode"),
    }
    if fields.get("allow_insecure") in (True, "1", "true", 1):
        q["allowInsecure"] = "1"
    if not q["mode"]:
        q.pop("mode")
    return q


def entry_from_fields(kind: str, fields: dict) -> dict:
    if kind not in FORM_KINDS or not isinstance(fields, dict):
        raise ParseError("unsupported")
    label = text_field(fields, "label", 80)
    if kind == "xray":
        try:
            obj = json.loads(text_field(fields, "json", 20000))
        except ValueError:
            raise ParseError("bad_json")
        entry = parse_config(obj)
        if label:
            entry["label"] = label
        return entry
    host = text_field(fields, "host")
    if not host or any(ch in host for ch in " /?#@"):
        raise ParseError("bad_link")
    port = port_field(fields)
    label = label or f"{host}:{port}"
    address = host.strip("[]")
    if kind == "http":
        user, password = text_field(fields, "user"), text_field(fields, "password")
        auth = f"{quote(user, safe='')}:{quote(password, safe='')}@" if user else ""
        shown = f"[{address}]" if ":" in address else address
        return make_entry("http", label, url=f"http://{auth}{shown}:{port}")
    if kind == "socks5":
        server = {"address": address, "port": port}
        if text_field(fields, "user"):
            server["users"] = [{"user": text_field(fields, "user"), "pass": text_field(fields, "password")}]
        return make_entry("socks5", label, outbound={"protocol": "socks", "settings": {"servers": [server]}})
    if kind == "shadowsocks":
        method, password = text_field(fields, "method"), text_field(fields, "password")
        if method not in SS_METHODS or not password:
            raise ParseError("bad_link")
        server = {"address": address, "port": port, "method": method, "password": password}
        return make_entry("shadowsocks", label, outbound={"protocol": "shadowsocks", "settings": {"servers": [server]}})
    if kind == "trojan":
        password = text_field(fields, "password")
        if not password:
            raise ParseError("bad_link")
        stream = build_stream(stream_query(fields), "tls")
        outbound = {"protocol": "trojan", "settings": {"servers": [{"address": address, "port": port, "password": password}]}, "streamSettings": stream}
        return make_entry("trojan", label, outbound=outbound)
    try:
        user_id = str(uuid.UUID(text_field(fields, "id")))
    except ValueError:
        raise ParseError("bad_uuid")
    stream = build_stream(stream_query(fields), "none")
    if kind == "vless":
        user = {"id": user_id, "encryption": text_field(fields, "encryption") or "none"}
        if text_field(fields, "flow"):
            user["flow"] = text_field(fields, "flow")
    else:
        try:
            alter = int(text_field(fields, "alter") or 0)
        except ValueError:
            raise ParseError("bad_link")
        user = {"id": user_id, "alterId": alter, "security": text_field(fields, "cipher") or "auto"}
    outbound = {"protocol": kind, "settings": {"vnext": [{"address": address, "port": port, "users": [user]}]}, "streamSettings": stream}
    return make_entry(kind, label, outbound=outbound)


def stream_fields(outbound: dict) -> dict:
    stream = outbound.get("streamSettings") or {}
    network = stream.get("network") or "tcp"
    security = stream.get("security") or "none"
    out = {"network": network, "security": security}
    tls = stream.get("tlsSettings") or {}
    reality = stream.get("realitySettings") or {}
    if security == "tls":
        out.update(sni=tls.get("serverName") or "", fp=tls.get("fingerprint") or "", alpn=",".join(tls.get("alpn") or []), allow_insecure=bool(tls.get("allowInsecure")))
    elif security == "reality":
        out.update(sni=reality.get("serverName") or "", fp=reality.get("fingerprint") or "", pbk=reality.get("publicKey") or "", sid=reality.get("shortId") or "", spx=reality.get("spiderX") or "")
    ws, grpc, upgrade, xhttp = (stream.get(k) or {} for k in ("wsSettings", "grpcSettings", "httpupgradeSettings", "xhttpSettings"))
    if network == "ws":
        out.update(path=ws.get("path") or "/", host_header=(ws.get("headers") or {}).get("Host", ""))
    elif network == "grpc":
        out.update(service=grpc.get("serviceName") or "", mode="multi" if grpc.get("multiMode") else "gun")
    elif network == "httpupgrade":
        out.update(path=upgrade.get("path") or "/", host_header=upgrade.get("host") or "")
    elif network == "xhttp":
        out.update(path=xhttp.get("path") or "/", host_header=xhttp.get("host") or "", mode=xhttp.get("mode") or "auto")
    return out


def entry_fields(entry: dict) -> dict:
    kind, label = entry["type"], entry["label"]
    if kind == "http":
        parts = urlsplit(entry["url"])
        return {"kind": "http", "label": label, "host": parts.hostname or "", "port": parts.port or "", "user": unquote(parts.username or ""), "password": unquote(parts.password or "")}
    outbound = entry.get("outbound") or {}
    settings = outbound.get("settings") or {}
    if kind == "socks5":
        server = (settings.get("servers") or [{}])[0]
        user = (server.get("users") or [{}])[0]
        return {"kind": "socks5", "label": label, "host": server.get("address", ""), "port": server.get("port", ""), "user": user.get("user", ""), "password": user.get("pass", "")}
    if kind == "shadowsocks":
        server = (settings.get("servers") or [{}])[0]
        return {"kind": kind, "label": label, "host": server.get("address", ""), "port": server.get("port", ""), "method": server.get("method", ""), "password": server.get("password", "")}
    if kind == "trojan":
        server = (settings.get("servers") or [{}])[0]
        return {"kind": kind, "label": label, "host": server.get("address", ""), "port": server.get("port", ""), "password": server.get("password", ""), **stream_fields(outbound)}
    if kind in ("vless", "vmess"):
        node = (settings.get("vnext") or [{}])[0]
        user = (node.get("users") or [{}])[0]
        base = {"kind": kind, "label": label, "host": node.get("address", ""), "port": node.get("port", ""), "id": user.get("id", ""), **stream_fields(outbound)}
        if kind == "vless":
            base.update(flow=user.get("flow", ""), encryption=user.get("encryption", "none"))
        else:
            base.update(alter=user.get("alterId", 0), cipher=user.get("security", "auto"))
        return base
    return {"kind": "xray", "label": label, "json": json.dumps(outbound, ensure_ascii=False, indent=2)}


SING_KINDS = {"vless": "vless", "vmess": "vmess", "trojan": "trojan", "shadowsocks": "shadowsocks", "socks": "socks5", "http": "http"}


def from_singbox(obj: dict) -> dict | None:
    outbounds = obj.get("outbounds")
    if not isinstance(outbounds, list):
        return None
    candidates = [o for o in outbounds if isinstance(o, dict) and o.get("type") in SING_KINDS and o.get("server")]
    if not candidates:
        return None
    ob = next((o for o in candidates if o.get("tag") == "proxy"), candidates[0])
    try:
        port = int(ob.get("server_port"))
    except (TypeError, ValueError):
        raise ParseError("bad_link")
    host = str(ob["server"])
    tls = ob.get("tls") if isinstance(ob.get("tls"), dict) else {}
    transport = ob.get("transport") if isinstance(ob.get("transport"), dict) else {}
    reality = tls.get("reality") if isinstance(tls.get("reality"), dict) else {}
    utls = tls.get("utls") if isinstance(tls.get("utls"), dict) else {}
    headers = transport.get("headers") if isinstance(transport.get("headers"), dict) else {}
    host_header = headers.get("Host") or transport.get("host") or ""
    if isinstance(host_header, list):
        host_header = host_header[0] if host_header else ""
    security = "none"
    if tls.get("enabled"):
        security = "reality" if reality.get("enabled") else "tls"
    q = {
        "type": str(transport.get("type") or "tcp"), "security": security,
        "sni": str(tls.get("server_name") or ""), "fp": str(utls.get("fingerprint") or ""),
        "alpn": ",".join(tls.get("alpn") or []) if isinstance(tls.get("alpn"), list) else "",
        "pbk": str(reality.get("public_key") or ""), "sid": str(reality.get("short_id") or ""),
        "path": str(transport.get("path") or "/"), "host": str(host_header),
        "serviceName": str(transport.get("service_name") or ""),
    }
    if tls.get("insecure"):
        q["allowInsecure"] = "1"
    kind = SING_KINDS[ob["type"]]
    label = str(obj.get("remarks") or ob.get("tag") or "") if str(ob.get("tag") or "") not in ("proxy", "") else ""
    label = label or f"{host}:{port}"
    if kind == "http":
        user, password = str(ob.get("username") or ""), str(ob.get("password") or "")
        auth = f"{quote(user, safe='')}:{quote(password, safe='')}@" if user else ""
        return make_entry("http", label, url=f"http://{auth}{host}:{port}")
    if kind == "socks5":
        server = {"address": host, "port": port}
        if ob.get("username"):
            server["users"] = [{"user": str(ob["username"]), "pass": str(ob.get("password") or "")}]
        return make_entry("socks5", label, outbound={"protocol": "socks", "settings": {"servers": [server]}})
    if kind == "shadowsocks":
        server = {"address": host, "port": port, "method": str(ob.get("method") or ""), "password": str(ob.get("password") or "")}
        return make_entry(kind, label, outbound={"protocol": "shadowsocks", "settings": {"servers": [server]}})
    stream = build_stream(q, "none")
    if kind == "trojan":
        server = {"address": host, "port": port, "password": str(ob.get("password") or "")}
        return make_entry(kind, label, outbound={"protocol": "trojan", "settings": {"servers": [server]}, "streamSettings": stream})
    try:
        user_id = str(uuid.UUID(str(ob.get("uuid") or "")))
    except ValueError:
        raise ParseError("bad_uuid")
    if kind == "vless":
        user = {"id": user_id, "encryption": "none"}
        if ob.get("flow"):
            user["flow"] = str(ob["flow"])
    else:
        user = {"id": user_id, "alterId": int(ob.get("alter_id") or 0), "security": str(ob.get("security") or "auto")}
    return make_entry(kind, label, outbound={"protocol": kind, "settings": {"vnext": [{"address": host, "port": port, "users": [user]}]}, "streamSettings": stream})


CHAT_PREFIX = re.compile(r"^\[\d{1,2}[./]\d{1,2}[./]\d{2,4}[^\]\n]*\][^:\n]{0,80}:[ \t]?", re.M)


def scan_items(text: str) -> list[tuple[str, object]]:
    text = CHAT_PREFIX.sub("", (text or "").lstrip("\ufeff"))
    decoder, pos, items = json.JSONDecoder(), 0, []
    while pos < len(text):
        while pos < len(text) and (text[pos].isspace() or text[pos] == ","):
            pos += 1
        if pos >= len(text):
            break
        if text[pos] in "{[":
            try:
                obj, end = decoder.raw_decode(text, pos)
                items.append(("json", obj))
                pos = end
                continue
            except ValueError:
                items.append(("badjson", None))
        end = text.find("\n", pos)
        end = len(text) if end < 0 else end
        line = text[pos:end].strip()
        pos = end + 1
        if line and not line.startswith("#") and line[0] not in "{[":
            items.append(("line", line))
    return items


def parse_config(obj) -> dict:
    if not isinstance(obj, dict):
        raise ParseError("bad_config")
    outbound = None
    if isinstance(obj.get("outbounds"), list):
        candidates = [o for o in obj["outbounds"] if isinstance(o, dict) and o.get("protocol") and o["protocol"] not in SKIP_PROTOCOLS]
        outbound = next((o for o in candidates if o.get("tag") == "proxy"), candidates[0] if candidates else None)
        if outbound is None:
            converted = from_singbox(obj)
            if converted is not None:
                return converted
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
    for _ in range(3):
        if not text or text[0] in "{[" or "://" in text[:4000]:
            return text
        compact = re.sub(r"\s+", "", text).replace("-", "+").replace("_", "/")
        try:
            raw = base64.b64decode(compact + "=" * (-len(compact) % 4)).decode("utf-8", errors="ignore").strip().lstrip("\ufeff")
        except ValueError:
            return text
        if not raw:
            return text
        text = raw
    return text





def parse_input(text: str) -> tuple[list[dict], list[dict], list[tuple[int, str]]]:
    items = scan_items(text)
    if not items:
        return [], [{"code": "empty", "n": 0}], []
    entries, errors, subs = [], [], []
    for n, (kind, value) in enumerate(items, 1):
        try:
            if kind == "badjson":
                raise ParseError("bad_json")
            if kind == "json":
                for obj in value if isinstance(value, list) else [value]:
                    entries.append(parse_config(obj))
                continue
            line = unwrap_link(value)
            if is_sub_url(line):
                subs.append((n, line))
            else:
                entries.append(parse_link(line))
        except ParseError as e:
            errors.append({"code": e.code, "n": n})
    return entries, errors, subs


class SubError(RuntimeError):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(code)
        self.code = code
        self.detail = detail[:160]


async def fetch_body(url: str, agent: str, via: str | None, hwid: str = "") -> str:
    headers = {"Accept": "*/*"}
    if agent:
        headers["User-Agent"] = agent
    if hwid and agent.startswith("Happ"):
        headers.update({"x-hwid": hwid, "x-device-os": "Android", "x-ver-os": "14", "x-device-model": "Pixel 7"})
    timeout = aiohttp.ClientTimeout(total=SUB_TIMEOUT, connect=8)
    async with aiohttp.ClientSession(timeout=timeout, headers=headers, skip_auto_headers=() if agent else ("User-Agent",)) as session:
        async with session.get(url, proxy=via) as resp:
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status}")
            data = await resp.content.read(SUB_MAX_BYTES + 1)
            if len(data) > SUB_MAX_BYTES:
                raise SubError("sub_too_large")
            return data.decode("utf-8", errors="replace")


async def resolve_url(url: str, via: str | None = None) -> str:
    if not url.lower().startswith("happ://crypt5/"):
        return url
    try:
        return await happ_crypt.resolve(url, via)
    except happ_crypt.CryptError as e:
        raise SubError(e.code)


async def load_subscription(url: str, via: str | None = None, hwid: str = "") -> tuple[list[dict], int]:
    url = await resolve_url(url, via)
    last_code, last_detail = "sub_fetch_failed", ""
    for route in ((None, via) if via else (None,)):
        for agent in SUB_AGENTS:
            try:
                body = await fetch_body(url, agent, route, hwid)
            except SubError as e:
                last_code, last_detail = e.code, e.detail
                break
            except RuntimeError as e:
                last_code, last_detail = "sub_fetch_failed", str(e)
                continue
            except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
                last_code, last_detail = "sub_fetch_failed", type(e).__name__
                break
            head = body.lstrip()[:200].lower()
            if head.startswith(("<!doctype", "<html")):
                last_code, last_detail = "sub_html", ""
                continue
            entries, skipped = parse_subscription(body)
            if entries:
                return entries, skipped
            last_code, last_detail = "sub_empty", f"skipped {skipped}"
    raise SubError(last_code, last_detail)


async def internet_up() -> bool:
    async def one(host: str, port: int) -> bool:
        try:
            _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), 3)
            writer.close()
            return True
        except (OSError, asyncio.TimeoutError):
            return False

    pending = [asyncio.ensure_future(one(h, p)) for h, p in NET_PROBES]
    try:
        for done in asyncio.as_completed(pending):
            if await done:
                return True
        return False
    finally:
        for task in pending:
            task.cancel()


def parse_subscription(body: str) -> tuple[list[dict], int]:
    text = decode_subscription(body)
    if text[:1] in "{[":
        entries, errors = parse_text(text)
    else:
        entries, errors = [], []
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]
        for n, line in enumerate(lines, 1):
            try:
                entries.append(parse_link(line))
            except ParseError as e:
                errors.append({"code": e.code, "n": n})
    return entries, len([e for e in errors if e["code"] != "empty"])


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
        self.checked = 0
        self.internet = True

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

    def replace(self, entry_id: str, fresh: dict) -> bool:
        for index, entry in enumerate(self.entries):
            if entry["id"] == entry_id:
                fresh["id"] = entry_id
                if entry.get("sub"):
                    fresh["sub"] = entry["sub"]
                self.entries[index] = fresh
                self.status.pop(entry_id, None)
                if self.active == entry_id:
                    self.active, self.url = "", None
                self.save()
                return True
        return False

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
                "down": int(entry.get("down", 0)),
            })
        subs = [{"id": s["id"], "label": s["label"], "count": s.get("count", 0), "updated": s.get("updated", 0)} for s in self.subs]
        return {"entries": rows, "subs": subs, "max": MAX_PROXIES, "binary": self.binary, "checked": self.checked, "internet": self.internet, "limit": DOWN_LIMIT}

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
        if ok and ("down" in entry or "down_since" in entry):
            entry.pop("down", None)
            entry.pop("down_since", None)
            self.dirty = True

    def account(self, entry: dict, ok: bool, now: float, internet: bool):
        last = entry.get("seen") or now
        entry["seen"] = int(now)
        if ok:
            entry.pop("down", None)
            entry.pop("down_since", None)
        elif internet:
            entry["down"] = int(entry.get("down", 0) + min(max(0.0, now - last), CHECK_GAP_CAP))
            entry.setdefault("down_since", int(now))
        self.dirty = True

    def cleanup(self) -> int:
        keep = [e for e in self.entries if e["id"] == self.active or e.get("down", 0) < DOWN_LIMIT]
        removed = len(self.entries) - len(keep)
        if removed:
            gone = {e["id"] for e in self.entries} - {e["id"] for e in keep}
            for entry_id in gone:
                self.status.pop(entry_id, None)
            self.entries = keep
            self.dirty = True
        return removed

    async def probe_group(self, entries: list[dict]) -> dict:
        if len(entries) > PROBE_CHUNK:
            merged: dict = {}
            for i in range(0, len(entries), PROBE_CHUNK):
                merged.update(await self.probe_group(entries[i:i + PROBE_CHUNK]))
            return merged
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

    async def probe_all(self, only_failed: bool = False) -> dict:
        async with self.probe_lock:
            results: dict = {}
            gate = asyncio.Semaphore(20)
            targets = [
                e for e in self.entries
                if not only_failed or e["id"] != self.active and not (self.status.get(e["id"]) or {}).get("ok")
            ]

            async def direct(entry):
                async with gate:
                    results[entry["id"]] = await probe(entry["url"], PROBE_TIMEOUT)

            plain = [e for e in targets if e["type"] == "http"]
            other = [e for e in targets if e["type"] != "http"]

            async def grouped():
                if other:
                    results.update(await self.probe_group(other))

            await asyncio.gather(grouped(), *(direct(e) for e in plain))
            failed = any(not r[0] for r in results.values())
            self.internet = await internet_up() if failed else True
            now = time.time()
            by_id = {e["id"]: e for e in self.entries}
            for entry_id, (ok, ms, error) in results.items():
                entry = by_id.get(entry_id)
                if entry is None:
                    continue
                if ok or self.internet:
                    self.record(entry_id, ok, ms, error)
                self.account(entry, ok, now, self.internet)
            self.checked = int(now)
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
            if not ok and not await internet_up():
                self.internet = False
                continue
            self.internet = True
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

    async def wait_recovery(self):
        while True:
            await asyncio.sleep(RECOVER_INTERVAL)
            if not self.entries:
                continue
            try:
                results = await self.probe_all()
            except Exception as e:
                logger.error(f"Background check failed: {e!r}")
                continue
            if any(r[0] for r in results.values()):
                return

    async def maintain(self, stop: asyncio.Event):
        delay = FIRST_CHECK_DELAY
        while True:
            try:
                await asyncio.wait_for(stop.wait(), delay)
                return
            except asyncio.TimeoutError:
                pass
            delay = MAINTAIN_INTERVAL
            if not self.entries:
                continue
            try:
                await self.probe_all(only_failed=bool(self.active))
                if self.cleanup():
                    self.flush()
            except Exception as e:
                logger.error(f"Background check failed: {e!r}")

    async def stop(self):
        await self.release()
        await self.prober.stop()
