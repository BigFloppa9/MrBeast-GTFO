import asyncio
import csv
import io
import json
import logging
import os
import time
from pathlib import Path
from .config import BASE_DIR
from urllib.parse import urlparse

import discord
from aiohttp import web

from . import __version__, happ_crypt
from .bot import scrub_discord_logs, set_log_channel
from .config import DEFAULT_REASON, LANGUAGES, MAX_STEPS, PRESETS, RETENTION_DAYS, effective_reason, ladder_steps, step_reason, steps_for
from .consolelog import console
from .logstore import read_image
from .runner import clean_token, runner, validate_token
from .security import CODE_TTL, MAX_HINT, MIN_PASSWORD_LENGTH, QUESTION_IDS
from .images import cached_image
from .network import lan_addresses
from .proxy import FORM_KINDS, ParseError, SubError, entry_fields, entry_from_fields, load_subscription, parse_input, resolve_url
from .state import state
from .theme import CONTENT_TYPES as BG_TYPES, ensure_background
from .updater import apply as apply_update, check as check_update, history as update_history
from .utils import apply_patch, fmt_duration, sanitize_settings

logger = logging.getLogger("mrbeast.web")

STATIC_DIR = Path(__file__).resolve().parent / "static"
COOKIE = "mb_session"
PUBLIC_API = {
    "/api/state", "/api/setup", "/api/login", "/api/kos-bg",
    "/api/forgot/start", "/api/forgot/verify", "/api/forgot/finish", "/api/forgot/answers",
}
CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
    "img-src 'self' data: https://sun1-13.userapi.com; "
    "base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
)
CONTENT_TYPES = {"png": "image/png", "jpg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}


def ok(**data) -> web.Response:
    return web.json_response({"ok": True, **data})


def fail(code: str, status: int = 400, **extra) -> web.Response:
    return web.json_response({"ok": False, "error": code, **extra}, status=status)


async def read_body(request: web.Request) -> dict:
    try:
        data = await request.json()
    except ValueError:
        raise web.HTTPBadRequest(text="bad json")
    if not isinstance(data, dict):
        raise web.HTTPBadRequest(text="bad json")
    return data


def attach_session(response: web.Response):
    token = state.sessions.create()
    response.set_cookie(COOKIE, token, httponly=True, samesite="Strict", max_age=43200, path="/")


def precheck(request: web.Request) -> web.Response | None:
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin = request.headers.get("Origin")
        if origin and urlparse(origin).netloc != request.host:
            return fail("forbidden", 403)
        if request.content_type != "application/json":
            return fail("bad_request", 400)
    if request.path.startswith("/api/") and request.path not in PUBLIC_API:
        if not state.sessions.valid(request.cookies.get(COOKIE)):
            return fail("unauthorized", 401)
    return None


@web.middleware
async def guard(request: web.Request, handler):
    response = precheck(request)
    if response is None:
        try:
            response = await handler(request)
        except web.HTTPException as exc:
            response = exc
    response.headers["Content-Security-Policy"] = CSP
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    if request.path.startswith("/api/") and not request.path.startswith("/api/image/"):
        response.headers["Cache-Control"] = "no-store"
    return response


async def index(request: web.Request):
    return web.FileResponse(STATIC_DIR / "index.html", headers={"Cache-Control": "no-cache"})


async def static_file(request: web.Request):
    name = request.match_info["name"]
    if name not in ("app.js", "app.css"):
        raise web.HTTPNotFound()
    return web.FileResponse(STATIC_DIR / name, headers={"Cache-Control": "no-cache"})


async def api_state(request: web.Request):
    return ok(
        configured=state.auth.configured,
        authed=state.sessions.valid(request.cookies.get(COOKIE)),
        panel_lang=state.config.panel_lang,
        bot_lang=state.config.bot_lang,
        min_password=MIN_PASSWORD_LENGTH,
    )


def password_error(password, repeat) -> str | None:
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        return "password_short"
    if password != repeat:
        return "password_mismatch"
    return None


async def api_setup(request: web.Request):
    if state.auth.configured:
        return fail("already_configured", 409)
    data = await read_body(request)
    token = clean_token(data.get("token"))
    if not token:
        return fail("token_empty")
    err = password_error(data.get("password"), data.get("repeat"))
    if err:
        return fail(err)
    valid, reason = await validate_token(token)
    if not valid and reason == "token_invalid":
        return fail(reason)
    await asyncio.to_thread(state.auth.set_password, data["password"])
    state.auth.set_token(token)
    state.config.set_languages(bot_lang=data.get("bot_lang"), panel_lang=data.get("panel_lang"))
    await runner.start(token)
    response = ok(warning="" if valid else reason)
    attach_session(response)
    return response


async def api_login(request: web.Request):
    if not state.auth.configured:
        return fail("not_configured", 409)
    key = request.remote or "unknown"
    locked = state.limiter.locked_for(key)
    if locked:
        return fail("locked", 429, seconds=locked)
    data = await read_body(request)
    password = data.get("password")
    good = isinstance(password, str) and await asyncio.to_thread(state.auth.verify_password, password)
    if not good:
        state.limiter.fail(key)
        attempts = state.limiter.count(key)
        hint = state.auth.recovery_view()["hint"] if attempts >= 2 else ""
        return fail("bad_password", 401, attempts=attempts, hint=hint)
    state.limiter.reset(key)
    response = ok()
    attach_session(response)
    return response


async def api_logout(request: web.Request):
    state.sessions.destroy(request.cookies.get(COOKIE))
    response = ok()
    response.del_cookie(COOKIE, path="/")
    return response


def reinstall_info() -> dict:
    termux = bool(os.environ.get("TERMUX_VERSION"))
    name = BASE_DIR.name
    parent = "~" if termux and BASE_DIR.parent == Path.home() else str(BASE_DIR.parent)
    install = "pkg install -y git && " if termux else ""
    command = f'cd {parent} && rm -rf "{name}" && {install}git clone https://github.com/BigFloppa9/MrBeast-GTFO "{name}" && cd "{name}" && bash install.sh'
    return {"env": "termux" if termux else "other", "command": command}


async def api_forgot_start(request: web.Request):
    if not state.auth.configured:
        return fail("not_configured", 409)
    linked = bool(state.config.moderators)
    if linked:
        state.reset.open()
    questions = state.auth.recovery_view()["questions"]
    extra = {} if linked or questions else {"reinstall": reinstall_info()}
    return ok(linked=linked, questions=questions, **extra)


async def api_forgot_answers(request: web.Request):
    key = "reset:" + (request.remote or "unknown")
    locked = state.limiter.locked_for(key)
    if locked:
        return fail("locked", 429, seconds=locked)
    data = await read_body(request)
    good = await asyncio.to_thread(state.auth.verify_answers, data.get("answers"))
    if not good:
        state.limiter.fail(key)
        return fail("answers_invalid", 400)
    state.limiter.reset(key)
    return ok(reset_token=state.reset.grant())


async def api_forgot_verify(request: web.Request):
    key = "reset:" + (request.remote or "unknown")
    locked = state.limiter.locked_for(key)
    if locked:
        return fail("locked", 429, seconds=locked)
    data = await read_body(request)
    token = state.reset.verify(str(data.get("code") or ""))
    if token is None:
        state.limiter.fail(key)
        return fail("code_invalid", 400)
    state.limiter.reset(key)
    return ok(reset_token=token)


async def api_forgot_finish(request: web.Request):
    data = await read_body(request)
    err = password_error(data.get("password"), data.get("repeat"))
    if err:
        return fail(err)
    if not state.reset.redeem(str(data.get("reset_token") or "")):
        return fail("reset_expired", 400)
    await asyncio.to_thread(state.auth.set_password, data["password"])
    state.sessions.clear()
    return ok()


async def api_status(request: web.Request):
    return ok(
        bot=runner.snapshot(),
        config={"bot_lang": state.config.bot_lang, "panel_lang": state.config.panel_lang},
        moderators=[{"id": str(m["id"]), "name": m["name"]} for m in state.config.moderators],
        reg={"active": state.reg_code.active(), "remaining": state.reg_code.remaining()},
        network={"port": state.port, "addresses": lan_addresses()},
        bot_state=state.config.bot_state,
        token_ready=state.auth.get_token() is not None,
    )


async def api_logs(request: web.Request):
    try:
        after = int(request.query.get("after", "0"))
    except ValueError:
        after = 0
    return ok(logs=state.logs.since(after))


async def api_image(request: web.Request):
    name = request.match_info["name"]
    data = await asyncio.to_thread(read_image, name)
    if data is None:
        raise web.HTTPNotFound()
    return web.Response(
        body=data,
        headers={
            "Content-Type": CONTENT_TYPES[name.rsplit(".", 1)[1]],
            "Cache-Control": "private, max-age=31536000, immutable",
            "Content-Disposition": "inline",
        },
    )


def find_guild(request: web.Request) -> discord.Guild | None:
    bot = runner.bot
    if not bot or not bot.is_ready():
        return None
    try:
        return bot.get_guild(int(request.match_info["gid"]))
    except ValueError:
        return None


def preview_steps(s: dict) -> dict:
    lg = state.config.bot_lang
    shown = {}
    for preset in ("ladder", "ladder_ban"):
        trial = dict(s, punish_preset=preset)
        steps = steps_for(trial)
        shown[preset] = [dict(step, reason=step_reason(trial, i, len(steps), lg)) for i, step in enumerate(steps)]
    return shown


def serialize_settings(guild: discord.Guild) -> dict:
    s = state.settings.get(guild.id)
    reason = s.get("timeout_reason") or ""
    if reason in DEFAULT_REASON.values():
        reason = ""
    return {
        "timeout_reason": reason,
        "timeout": fmt_duration(s["timeout_duration"]),
        "delete_window": fmt_duration(s["delete_window"]),
        "auto_min_images": s["auto_min_images"],
        "auto_min_channels": s["auto_min_channels"],
        "auto_window_seconds": s["auto_window_seconds"],
        "log_channel": str(s["log_channel"] or ""),
        "punish_preset": s["punish_preset"],
        "custom_steps": s["custom_steps"],
        "warn_reset_days": s["warn_reset_days"],
        "dm_reason": bool(s["dm_reason"]),
        "preview": preview_steps(s),
        "max_steps": MAX_STEPS,
    }


async def api_guild_get(request: web.Request):
    guild = find_guild(request)
    if guild is None:
        return fail("guild_unavailable", 404)
    return ok(
        settings=serialize_settings(guild),
        default_reason=DEFAULT_REASON[state.config.bot_lang],
        channels=[{"id": str(c.id), "name": c.name} for c in guild.text_channels],
    )


async def api_guild_put(request: web.Request):
    guild = find_guild(request)
    if guild is None:
        return fail("guild_unavailable", 404)
    data = await read_body(request)
    s = state.settings.get(guild.id)
    trial = s.copy()
    errors = apply_patch(trial, data)
    if errors:
        return fail("validation", errors=errors)

    if "log_channel" in data:
        raw = str(data["log_channel"] or "").strip()
        if not raw or raw == "0":
            trial["log_channel"] = 0
        else:
            try:
                channel = guild.get_channel(int(raw))
            except ValueError:
                channel = None
            if not isinstance(channel, discord.TextChannel):
                return fail("channel_invalid")
            missing = await set_log_channel(guild, channel)
            if missing:
                return fail("log_missing_perms", missing=missing)
            trial["log_channel"] = channel.id

    s.update(trial)
    state.settings.save()
    return ok(settings=serialize_settings(guild))


async def api_config_put(request: web.Request):
    data = await read_body(request)
    for key in ("bot_lang", "panel_lang"):
        if key in data and data[key] not in LANGUAGES:
            return fail("lang_invalid")
    state.config.set_languages(bot_lang=data.get("bot_lang"), panel_lang=data.get("panel_lang"))
    return ok(config={"bot_lang": state.config.bot_lang, "panel_lang": state.config.panel_lang})


async def api_token_put(request: web.Request):
    key = "token:" + (request.remote or "unknown")
    locked = state.limiter.locked_for(key)
    if locked:
        return fail("locked", 429, seconds=locked)
    data = await read_body(request)
    password = data.get("password")
    good = isinstance(password, str) and await asyncio.to_thread(state.auth.verify_password, password)
    if not good:
        state.limiter.fail(key)
        return fail("bad_password", 401)
    state.limiter.reset(key)
    token = clean_token(data.get("token"))
    if not token:
        return fail("token_empty")
    valid, reason = await validate_token(token)
    if not valid and reason == "token_invalid":
        return fail(reason)
    state.auth.set_token(token)
    await runner.start(token)
    return ok(warning="" if valid else reason)


async def api_moderator_code(request: web.Request):
    return ok(code=state.reg_code.issue(), ttl=CODE_TTL)


async def api_moderator_delete(request: web.Request):
    try:
        user_id = int(request.match_info["uid"])
    except ValueError:
        return fail("moderator_missing", 404)
    if not state.config.remove_moderator(user_id):
        return fail("moderator_missing", 404)
    return ok(moderators=[{"id": str(m["id"]), "name": m["name"]} for m in state.config.moderators])


async def api_erase(request: web.Request):
    data = await read_body(request)
    query = str(data.get("query") or "").strip()
    if not query.lstrip("@"):
        return fail("query_empty")
    confirm = bool(data.get("confirm"))
    found = state.logs.matches(query)
    count = state.logs.erase(query, False)
    strikes = sum(1 for users in state.strikes.data.values() for uid in users if uid in found["ids"])
    if not confirm:
        return ok(count=count + strikes, strikes=strikes)
    count = state.logs.erase(query, True)
    removed = state.strikes.forget(found["ids"])
    console.scrub(found["ids"] | found["names"] | ({query.lstrip("@")} if len(query.lstrip("@")) >= 3 else set()))
    scrubbed = await scrub_discord_logs(runner.bot, found["ids"], found["refs"])
    return ok(count=count + removed, strikes=removed, discord=scrubbed)


async def api_update_check(request: web.Request):
    result = await check_update()
    return ok(**{k: v for k, v in result.items() if k != "ok"}) if result["ok"] else fail(result["error"], detail=result.get("detail", ""))


async def api_update_apply(request: web.Request):
    data = await read_body(request)
    password = data.get("password")
    if not (isinstance(password, str) and await asyncio.to_thread(state.auth.verify_password, password)):
        return fail("bad_password", 401)
    if state.update["running"]:
        return fail("update_running", 409)
    asyncio.create_task(apply_update())
    return ok()


async def api_update_info(request: web.Request):
    result = await update_history()
    return ok(**{k: v for k, v in result.items() if k != "ok"}, git=result["ok"])


async def api_console(request: web.Request):
    try:
        limit = max(1, min(int(request.query.get("limit", "100")), 500))
    except ValueError:
        limit = 100
    return ok(lines=console.lines(limit))


def console_text(item: dict) -> str:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item["ts"]))
    return f"{stamp} {item['level']} {item['name']}: {item['msg']}"


async def api_console_export(request: web.Request):
    fmt = request.query.get("format", "txt")
    items = console.lines(0, request.query.get("scope") == "session")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    if fmt == "json":
        body, kind, ext = json.dumps(items, ensure_ascii=False, indent=1), "application/json", "json"
    elif fmt == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["time", "level", "logger", "message"])
        for item in items:
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item["ts"])), item["level"], item["name"], item["msg"]])
        body, kind, ext = buffer.getvalue(), "text/csv", "csv"
    else:
        body, kind, ext = "\n".join(console_text(i) for i in items) + "\n", "text/plain", "txt"
    return web.Response(
        body=body.encode("utf-8"),
        headers={"Content-Type": kind + "; charset=utf-8", "Content-Disposition": f'attachment; filename="mrbeast-console-{stamp}.{ext}"'},
    )


async def api_security_get(request: web.Request):
    return ok(**state.auth.recovery_view(), ids=list(QUESTION_IDS), max_hint=MAX_HINT, linked=bool(state.config.moderators))


async def api_security_put(request: web.Request):
    key = "security:" + (request.remote or "unknown")
    locked = state.limiter.locked_for(key)
    if locked:
        return fail("locked", 429, seconds=locked)
    data = await read_body(request)
    password = data.get("password")
    if not (isinstance(password, str) and await asyncio.to_thread(state.auth.verify_password, password)):
        state.limiter.fail(key)
        return fail("bad_password", 401)
    state.limiter.reset(key)
    questions = data.get("questions")
    hint = data.get("hint")
    if not isinstance(questions, list) or not all(isinstance(q, dict) for q in questions) or not isinstance(hint, str):
        return fail("bad_request")
    error = await asyncio.to_thread(state.auth.set_recovery, questions, hint)
    if error:
        return fail(error)
    return ok(**state.auth.recovery_view())


async def api_data_export(request: web.Request):
    data = await read_body(request)
    passphrase = data.get("passphrase")
    if not isinstance(passphrase, str) or len(passphrase) < 6:
        return fail("passphrase_short")
    state.strikes.expire({str(gid): s["warn_reset_days"] for gid, s in state.settings.data.items()})
    block = await asyncio.to_thread(state.strikes.export_block, passphrase)
    settings = {str(gid): s for gid, s in state.settings.data.items()}
    return ok(export={
        "app": "mrbeast-gtfo", "format": 1, "version": __version__, "exported": int(time.time()),
        "config": {"bot_lang": state.config.bot_lang, "panel_lang": state.config.panel_lang},
        "settings": settings, "strikes": block,
    })


async def api_data_import(request: web.Request):
    data = await read_body(request)
    export, passphrase = data.get("export"), data.get("passphrase")
    if not isinstance(export, dict) or export.get("app") != "mrbeast-gtfo" or export.get("format") != 1 or not isinstance(passphrase, str):
        return fail("import_invalid")
    incoming = export.get("settings")
    if not isinstance(incoming, dict):
        return fail("import_invalid")
    cleaned = {}
    for gid, raw in incoming.items():
        if str(gid).isdigit():
            cleaned[int(gid)] = sanitize_settings(raw)
    resets = {str(g): s["warn_reset_days"] for g, s in cleaned.items()}
    for g, s in state.settings.data.items():
        resets.setdefault(str(g), s["warn_reset_days"])
    try:
        merged = await asyncio.to_thread(state.strikes.import_block, export.get("strikes") or {}, passphrase, resets)
    except ValueError as e:
        return fail(str(e))
    state.settings.data.update(cleaned)
    state.settings.save()
    cfg = export.get("config") if isinstance(export.get("config"), dict) else {}
    state.config.set_languages(bot_lang=cfg.get("bot_lang"), panel_lang=cfg.get("panel_lang"))
    return ok(guilds=len(cleaned), strikes=merged)


async def api_update_status(request: web.Request):
    return ok(**state.update)


async def api_kos_bg(request: web.Request):
    path = await ensure_background()
    if path is None:
        raise web.HTTPNotFound()
    return web.FileResponse(path, headers={"Content-Type": BG_TYPES[path.suffix[1:]], "Cache-Control": "public, max-age=86400"})


async def restart_bot():
    token = state.auth.get_token()
    if token:
        await runner.start(token)


async def api_img(request: web.Request):
    kind = request.match_info["kind"]
    url = runner.image_url(kind, request.match_info.get("gid", ""))
    path = await cached_image(url) if url else None
    if path is None:
        raise web.HTTPNotFound()
    return web.FileResponse(path, headers={"Content-Type": BG_TYPES[path.suffix[1:]], "Cache-Control": "private, max-age=3600"})


async def api_bot(request: web.Request):
    action = request.match_info["action"]
    config = state.config
    if action == "pause":
        config.set_bot_state("paused")
    elif action == "resume":
        config.set_bot_state("running")
    elif action == "stop":
        config.set_bot_state("stopped")
        await runner.stop()
    elif action in ("start", "restart"):
        if config.bot_state == "stopped":
            config.set_bot_state("running")
        await restart_bot()
    else:
        raise web.HTTPNotFound()
    return ok(bot=runner.snapshot(), bot_state=config.bot_state)


async def read_subscription(url: str):
    if not url.lower().startswith(("http://", "https://")) or len(url) > 2000:
        return None, fail("sub_invalid")
    try:
        return await load_subscription(url, state.proxy_url, state.config.hwid), None
    except SubError as e:
        return None, fail(e.code, detail=e.detail)


async def api_sub_add(request: web.Request):
    url = str((await read_body(request)).get("url") or "").strip()
    parsed, error = await read_subscription(url)
    if error:
        return error
    entries, skipped = parsed
    known = next((x for x in state.proxies.subs if x["url"] == url), None)
    state.proxies.set_subscription(url, entries, known["id"] if known else None)
    await restart_bot()
    return ok(skipped=skipped, **state.proxies.view())


async def api_sub_update(request: web.Request):
    sub = next((s for s in state.proxies.subs if s["id"] == request.match_info["sid"]), None)
    if sub is None:
        return fail("proxy_missing", 404)
    parsed, error = await read_subscription(sub["url"])
    if error:
        return error
    entries, skipped = parsed
    state.proxies.set_subscription(sub["url"], entries, sub["id"])
    await restart_bot()
    return ok(skipped=skipped, **state.proxies.view())


async def api_sub_delete(request: web.Request):
    if not state.proxies.remove_subscription(request.match_info["sid"]):
        return fail("proxy_missing", 404)
    await restart_bot()
    return ok(**state.proxies.view())


async def api_proxy_get(request: web.Request):
    return ok(**state.proxies.view())


async def api_proxy_add(request: web.Request):
    data = await read_body(request)
    entries, errors, subs = parse_input(str(data.get("text") or ""))
    added = state.proxies.add(entries) if entries else 0
    full = bool(entries) and not added
    for n, url in subs:
        try:
            url = await resolve_url(url, state.proxy_url)
            loaded, _ = await load_subscription(url, state.proxy_url, state.config.hwid)
        except SubError as e:
            errors.append({"code": e.code, "n": n, "detail": e.detail})
            continue
        known = next((x for x in state.proxies.subs if x["url"] == url), None)
        sub = state.proxies.set_subscription(url, loaded, known["id"] if known else None)
        added += sub.get("count", 0)
        if len(loaded) > sub.get("count", 0):
            errors.append({"code": "sub_truncated", "n": n, "detail": str(len(loaded) - sub.get("count", 0))})
    if not added:
        return fail("proxy_limit" if full else "proxy_invalid", errors=errors)
    await restart_bot()
    return ok(added=added, errors=errors, **state.proxies.view())


async def api_proxy_form_add(request: web.Request):
    data = await read_body(request)
    try:
        entry = entry_from_fields(str(data.get("kind") or ""), data.get("fields"))
    except ParseError as e:
        return fail(e.code)
    if not state.proxies.add([entry]):
        return fail("proxy_limit")
    await restart_bot()
    return ok(**state.proxies.view())


async def api_proxy_item(request: web.Request):
    entry = next((e for e in state.proxies.entries if e["id"] == request.match_info["pid"]), None)
    if entry is None:
        return fail("proxy_missing", 404)
    return ok(fields=entry_fields(entry), kinds=list(FORM_KINDS))


async def api_proxy_edit(request: web.Request):
    data = await read_body(request)
    try:
        fresh = entry_from_fields(str(data.get("kind") or ""), data.get("fields"))
    except ParseError as e:
        return fail(e.code)
    if not state.proxies.replace(request.match_info["pid"], fresh):
        return fail("proxy_missing", 404)
    await restart_bot()
    return ok(**state.proxies.view())


async def api_proxy_delete(request: web.Request):
    if not state.proxies.remove(request.match_info["pid"]):
        return fail("proxy_missing", 404)
    await restart_bot()
    return ok(**state.proxies.view())


def create_app() -> web.Application:
    app = web.Application(middlewares=[guard], client_max_size=1024 * 1024)
    app.router.add_get("/", index)
    app.router.add_get("/static/{name}", static_file)
    app.router.add_get("/api/state", api_state)
    app.router.add_post("/api/setup", api_setup)
    app.router.add_post("/api/login", api_login)
    app.router.add_post("/api/logout", api_logout)
    app.router.add_post("/api/forgot/start", api_forgot_start)
    app.router.add_post("/api/forgot/verify", api_forgot_verify)
    app.router.add_post("/api/forgot/finish", api_forgot_finish)
    app.router.add_post("/api/forgot/answers", api_forgot_answers)
    app.router.add_get("/api/security", api_security_get)
    app.router.add_put("/api/security", api_security_put)
    app.router.add_get("/api/console", api_console)
    app.router.add_get("/api/console/export", api_console_export)
    app.router.add_post("/api/data/export", api_data_export)
    app.router.add_post("/api/data/import", api_data_import)
    app.router.add_get("/api/update/info", api_update_info)
    app.router.add_delete("/api/moderator/{uid}", api_moderator_delete)
    app.router.add_get("/api/status", api_status)
    app.router.add_get("/api/logs", api_logs)
    app.router.add_get("/api/image/{name}", api_image)
    app.router.add_get("/api/guilds/{gid}/settings", api_guild_get)
    app.router.add_put("/api/guilds/{gid}/settings", api_guild_put)
    app.router.add_put("/api/config", api_config_put)
    app.router.add_put("/api/token", api_token_put)
    app.router.add_post("/api/moderator/code", api_moderator_code)
    app.router.add_post("/api/privacy/erase", api_erase)
    app.router.add_get("/api/kos-bg", api_kos_bg)
    app.router.add_get("/api/img/{kind}", api_img)
    app.router.add_get("/api/img/{kind}/{gid}", api_img)
    app.router.add_post("/api/bot/{action}", api_bot)
    app.router.add_post("/api/proxy/sub", api_sub_add)
    app.router.add_post("/api/proxy/sub/{sid}/update", api_sub_update)
    app.router.add_delete("/api/proxy/sub/{sid}", api_sub_delete)
    app.router.add_get("/api/proxy", api_proxy_get)
    app.router.add_post("/api/proxy", api_proxy_add)
    app.router.add_post("/api/proxy/form", api_proxy_form_add)
    app.router.add_get("/api/proxy/{pid}", api_proxy_item)
    app.router.add_put("/api/proxy/{pid}", api_proxy_edit)
    app.router.add_delete("/api/proxy/{pid}", api_proxy_delete)
    app.router.add_get("/api/update/check", api_update_check)
    app.router.add_post("/api/update/apply", api_update_apply)
    app.router.add_get("/api/update/status", api_update_status)
    return app
