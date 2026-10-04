import asyncio
import logging
import os
import signal
import socket
import sys

from aiohttp import web

from .config import BASE_DIR
from .state import state
from .runner import runner
from .web import create_app

BANNER = {
    "en": {
        "title": "MrBeast GTFO panel is running",
        "network": "Open from any device in your network:",
        "local": "Open on this device:",
        "setup": "First launch: finish the setup in the browser.",
        "login": "Sign in with your panel password.",
        "stop": "Press Ctrl+C to stop.",
        "no_port": "No free port found in range {first}-{last}.",
    },
    "ru": {
        "title": "Панель MrBeast GTFO запущена",
        "network": "Откройте с любого устройства в вашей сети:",
        "local": "Откройте на этом устройстве:",
        "setup": "Первый запуск: завершите настройку в браузере.",
        "login": "Войдите с паролем от панели.",
        "stop": "Для остановки нажмите Ctrl+C.",
        "no_port": "Не найден свободный порт в диапазоне {first}-{last}.",
    },
}


def local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("10.255.255.255", 1))
        return sock.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "127.0.0.1"
    finally:
        sock.close()


async def bind(site_runner: web.AppRunner, host: str, first: int, attempts: int = 100) -> int | None:
    for port in range(first, first + attempts):
        site = web.TCPSite(site_runner, host, port)
        try:
            await site.start()
            return port
        except OSError:
            continue
    return None


def print_banner(port: int):
    text = BANNER[state.config.panel_lang]
    ip = local_ip()
    line = "─" * 52
    print(line)
    print(f" {text['title']}")
    print(line)
    print(f" {text['network']}")
    print(f"   http://{ip}:{port}")
    print(f" {text['local']}")
    print(f"   http://localhost:{port}")
    print(line)
    print(f" {text['login'] if state.auth.configured else text['setup']}")
    print(f" {text['stop']}")
    print(line, flush=True)


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)

    host = os.environ.get("MRBEAST_HOST", "0.0.0.0")
    try:
        first_port = int(os.environ.get("MRBEAST_PORT", "8080"))
    except ValueError:
        first_port = 8080

    site_runner = web.AppRunner(create_app(), access_log=None)
    await site_runner.setup()
    port = await bind(site_runner, host, first_port)
    if port is None:
        print(BANNER[state.config.panel_lang]["no_port"].format(first=first_port, last=first_port + 99))
        await site_runner.cleanup()
        return

    state.port = port
    print_banner(port)

    if state.auth.configured:
        token = state.auth.get_token()
        if token:
            await runner.start(token)

    stop = asyncio.Event()
    state.stop_event = stop
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except (NotImplementedError, RuntimeError):
            pass
    try:
        await stop.wait()
    finally:
        await runner.stop()
        await site_runner.cleanup()

    if state.restart:
        os.environ["MRBEAST_PORT"] = str(state.port)
        os.chdir(BASE_DIR)
        os.execv(sys.executable, [sys.executable, "-m", "mrbeast"])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
