import asyncio
import logging
import os
import signal
import sys

from aiohttp import web

from .config import BASE_DIR
from .network import lan_addresses
from .state import state
from .runner import runner
from .web import create_app

BANNER = {
    "en": {
        "title": "MrBeast GTFO panel is running",
        "network": "Open from another device in the same Wi-Fi network (use the address that matches your network):",
        "local": "Open on this device:",
        "changed": "Network address changed, use:",
        "hint": "If another device can't open the page, check the phone's IP in the router or Wi-Fi settings and make sure client isolation is off.",
        "setup": "First launch: finish the setup in the browser.",
        "login": "Sign in with your panel password.",
        "stop": "Press Ctrl+C to stop.",
        "no_port": "No free port found in range {first}-{last}.",
    },
    "ru": {
        "title": "Панель MrBeast GTFO запущена",
        "network": "Откройте с другого устройства в той же Wi-Fi сети (берите адрес, подходящий вашей сети):",
        "local": "Откройте на этом устройстве:",
        "changed": "Сетевой адрес изменился, используйте:",
        "hint": "Если другое устройство не открывает страницу, сверьте IP телефона в роутере или настройках Wi-Fi и убедитесь, что изоляция клиентов выключена.",
        "setup": "Первый запуск: завершите настройку в браузере.",
        "login": "Войдите с паролем от панели.",
        "stop": "Для остановки нажмите Ctrl+C.",
        "no_port": "Не найден свободный порт в диапазоне {first}-{last}.",
    },
}


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
    line = "─" * 52
    print(line)
    print(f" {text['title']}")
    print(line)
    print(f" {text['network']}")
    for item in lan_addresses() or [{"ip": "?", "iface": "", "kind": ""}]:
        tag = f"  [{item['iface']}]" if item["iface"] else ""
        print(f"   http://{item['ip']}:{port}{tag}")
    print(f" {text['hint']}")
    print(f" {text['local']}")
    print(f"   http://localhost:{port}")
    print(line)
    print(f" {text['login'] if state.auth.configured else text['setup']}")
    print(f" {text['stop']}")
    print(line, flush=True)


class QuietReconnects(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.name == "asyncio" and str(record.msg).startswith("Unclosed connection"):
            return False
        if record.name == "discord.client" and str(record.msg).startswith("Attempting a reconnect"):
            record.levelno, record.levelname, record.exc_info = logging.WARNING, "WARNING", None
        return True


async def watch_network(port: int, stop: asyncio.Event):
    known = {item["ip"] for item in lan_addresses()}
    text = BANNER[state.config.panel_lang]
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), 30)
        except asyncio.TimeoutError:
            current = lan_addresses()
            ips = {item["ip"] for item in current}
            if ips != known and ips:
                known = ips
                print(f"\n {text['changed']}")
                for item in current:
                    print(f"   http://{item['ip']}:{port}")


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
    quiet = QuietReconnects()
    for handler in logging.getLogger().handlers:
        handler.addFilter(quiet)

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

    if state.auth.configured and state.config.bot_state != "stopped":
        token = state.auth.get_token()
        if token:
            await runner.start(token)

    stop = asyncio.Event()
    state.stop_event = stop
    background = [asyncio.create_task(watch_network(port, stop)), asyncio.create_task(state.proxies.maintain(stop))]
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except (NotImplementedError, RuntimeError):
            pass
    try:
        await stop.wait()
    finally:
        for task in background:
            task.cancel()
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
