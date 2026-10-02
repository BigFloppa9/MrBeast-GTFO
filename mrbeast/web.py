import asyncio
import logging
from pathlib import Path
from urllib.parse import urlparse

import discord
from aiohttp import web

from .bot import set_log_channel
from .config import DEFAULT_REASON, LANGUAGES
from .logstore import image_path
from .runner import clean_token, runner, validate_token
from .security import CODE_TTL, MIN_PASSWORD_LENGTH
from .state import state
from .utils import apply_patch, fmt_duration

logger = logging.getLogger("mrbeast.web")

STATIC_DIR = Path(__file__).resolve().parent / "static"
COOKIE = "mb_session"
PUBLIC_API = {
    "/api/state", "/api/setup", "/api/login",
    "/api/forgot/start", "/api/forgot/verify", "/api/forgot/finish",
}
CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
    "img-src 'self' data: https://cdn.discordapp.com https://media.discordapp.net; "
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
    if not valid:
        return fail(reason)
    await asyncio.to_thread(state.auth.set_password, data["password"])
    state.auth.set_token(token)
    state.config.set_languages(bot_lang=data.get("bot_lang"), panel_lang=data.get("panel_lang"))
    await runner.start(token)
    response = ok()
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
        return fail("bad_password", 401)
    state.limiter.reset(key)
    response = ok()
    attach_session(response)
    return response


async def api_logout(request: web.Request):
    state.sessions.destroy(request.cookies.get(COOKIE))
    response = ok()
    response.del_cookie(COOKIE, path="/")
    return response


async def api_forgot_start(request: web.Request):
    if not state.auth.configured:
        return fail("not_configured", 409)
    linked = bool(state.config.moderator_id)
    if linked:
        state.reset.open()
    return ok(linked=linked)


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
        moderator={
            "linked": bool(state.config.moderator_id),
            "name": state.config.moderator_name,
            "id": str(state.config.moderator_id) if state.config.moderator_id else "",
        },
        reg={"active": state.reg_code.active(), "remaining": state.reg_code.remaining()},
        token_ready=state.auth.get_token() is not None,
    )


async def api_logs(request: web.Request):
    try:
        after = int(request.query.get("after", "0"))
    except ValueError:
        after = 0
    return ok(logs=state.logs.since(after))


async def api_image(request: web.Request):
    path = image_path(request.match_info["name"])
    if path is None:
        raise web.HTTPNotFound()
    return web.FileResponse(
        path,
        headers={
            "Content-Type": CONTENT_TYPES[path.suffix[1:]],
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
    if not valid:
        return fail(reason)
    state.auth.set_token(token)
    await runner.start(token)
    return ok()


async def api_moderator_code(request: web.Request):
    return ok(code=state.reg_code.issue(), ttl=CODE_TTL)


def create_app() -> web.Application:
    app = web.Application(middlewares=[guard], client_max_size=1024 * 64)
    app.router.add_get("/", index)
    app.router.add_get("/static/{name}", static_file)
    app.router.add_get("/api/state", api_state)
    app.router.add_post("/api/setup", api_setup)
    app.router.add_post("/api/login", api_login)
    app.router.add_post("/api/logout", api_logout)
    app.router.add_post("/api/forgot/start", api_forgot_start)
    app.router.add_post("/api/forgot/verify", api_forgot_verify)
    app.router.add_post("/api/forgot/finish", api_forgot_finish)
    app.router.add_get("/api/status", api_status)
    app.router.add_get("/api/logs", api_logs)
    app.router.add_get("/api/image/{name}", api_image)
    app.router.add_get("/api/guilds/{gid}/settings", api_guild_get)
    app.router.add_put("/api/guilds/{gid}/settings", api_guild_put)
    app.router.add_put("/api/config", api_config_put)
    app.router.add_put("/api/token", api_token_put)
    app.router.add_post("/api/moderator/code", api_moderator_code)
    return app
