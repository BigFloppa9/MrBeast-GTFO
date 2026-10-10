import asyncio
import os
import sys

from . import __version__
from .config import BASE_DIR
from .runner import runner
from .state import state

TERMUX_ENV = {
    "AIOHTTP_NO_EXTENSIONS": "1",
    "MULTIDICT_NO_EXTENSIONS": "1",
    "YARL_NO_EXTENSIONS": "1",
    "FROZENLIST_NO_EXTENSIONS": "1",
}


class UpdateError(Exception):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(code)
        self.code = code
        self.detail = detail[-300:]


async def run(*cmd: str, timeout: int = 60) -> tuple[int, str, str]:
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "PIP_NO_INPUT": "1"}
    if os.environ.get("TERMUX_VERSION"):
        env.update(TERMUX_ENV)
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, cwd=str(BASE_DIR), env=env,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
    except OSError as e:
        return 127, "", str(e)
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return 124, "", "timeout"
    return proc.returncode, out.decode(errors="replace").strip(), err.decode(errors="replace").strip()


async def upstream() -> str:
    code, ref, _ = await run("git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    return ref if code == 0 and ref else "origin/main"


async def check() -> dict:
    code, head, _ = await run("git", "rev-parse", "--short", "HEAD")
    if code:
        return {"ok": False, "error": "not_git"}
    code, _, err = await run("git", "fetch", "--quiet", "origin", timeout=90)
    if code:
        return {"ok": False, "error": "fetch_failed", "detail": err[-200:]}
    ref = await upstream()
    _, count, _ = await run("git", "rev-list", "--count", f"HEAD..{ref}")
    _, changes, _ = await run("git", "log", "--pretty=format:%h %s", "-n", "15", f"HEAD..{ref}")
    _, current, _ = await run("git", "log", "-1", "--pretty=format:%cs %s")
    _, dirty, _ = await run("git", "status", "--porcelain", "--untracked-files=no")
    return {
        "ok": True,
        "version": __version__,
        "head": head,
        "current": current,
        "behind": int(count or 0),
        "changes": changes.splitlines(),
        "dirty": bool(dirty),
    }


async def history(limit: int = 6) -> dict:
    code, head, _ = await run("git", "rev-parse", "--short", "HEAD")
    if code:
        return {"ok": False, "error": "not_git", "version": __version__}
    _, raw, _ = await run("git", "log", "-n", str(limit), "--pretty=format:%x1e%h%x1f%cs%x1f%s%x1f%b")
    commits = []
    for chunk in raw.split("\x1e"):
        if not chunk.strip():
            continue
        parts = (chunk.split("\x1f") + ["", "", "", ""])[:4]
        commits.append({"hash": parts[0].strip(), "date": parts[1].strip(), "title": parts[2].strip(), "body": parts[3].strip()})
    return {"ok": True, "version": __version__, "head": head, "commits": commits}


async def rollback(old: str):
    if old:
        await run("git", "reset", "--hard", old)


async def apply():
    status = state.update
    if status["running"]:
        return
    status.update(running=True, step="stopping", error="", detail="")
    old = ""
    try:
        _, old, _ = await run("git", "rev-parse", "HEAD")
        await runner.stop()
        status["step"] = "pulling"
        code, _, err = await run("git", "pull", "--ff-only", timeout=180)
        if code:
            raise UpdateError("pull_failed", err)
        status["step"] = "deps"
        pip = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        code, _, err = await run(*pip, timeout=900)
        if code and "externally-managed" in err:
            code, _, err = await run(*pip, "--break-system-packages", timeout=900)
        if code:
            raise UpdateError("deps_failed", err)
        status["step"] = "checking"
        code, _, err = await run(sys.executable, "-c", "import mrbeast.web, mrbeast.bot", timeout=90)
        if code:
            raise UpdateError("check_failed", err)
        status["step"] = "restarting"
        state.restart = True
        state.stop_event.set()
    except Exception as e:
        await rollback(old)
        code = e.code if isinstance(e, UpdateError) else "update_failed"
        detail = e.detail if isinstance(e, UpdateError) else str(e)[-300:]
        status.update(running=False, step="", error=code, detail=detail)
        token = state.auth.get_token()
        if token:
            await runner.start(token)
