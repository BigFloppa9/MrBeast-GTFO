import json
import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger("mrbeast.config")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("MRBEAST_DATA_DIR") or BASE_DIR / "data")
IMAGES_DIR = DATA_DIR / "images"
SETTINGS_FILE = DATA_DIR / "settings.json"
CONFIG_FILE = DATA_DIR / "config.json"
AUTH_FILE = DATA_DIR / "auth.json"
KEY_FILE = DATA_DIR / "secret.key"
LOGS_FILE = DATA_DIR / "logs.json"
PROXIES_FILE = DATA_DIR / "proxies.json"
BIN_DIR = DATA_DIR / "bin"
XRAY_DIR = DATA_DIR / "xray"

MAX_TIMEOUT_MINUTES = 28 * 1440
MAX_DELETE_WINDOW_MINUTES = 365 * 1440
MAX_REASON_LENGTH = 512
LANGUAGES = ("en", "ru")

DEFAULT_REASON = {
    "en": (
        "Hello! Your account has been compromised and you have likely been banned "
        "on many servers. We strongly recommend: change your passwords on all websites "
        "you use, revoke all active Discord sessions and other apps, enable two-factor "
        "authentication, and be cautious when downloading Roblox cheats from YouTube "
        "links. If you want a clean cheat site, use weao.gg. AND NEVER SCAN RANDOM QR-codes."
    ),
    "ru": (
        "Привет! Ваш аккаунт взломан, и вас, вероятно, уже заблокировали на многих серверах. "
        "Настоятельно рекомендуем: смените пароли на всех сайтах, завершите все активные сессии "
        "Discord и других приложений, включите двухфакторную аутентификацию и будьте осторожны "
        "при скачивании читов для Roblox по ссылкам с YouTube. Если нужен чистый сайт с читами, "
        "используйте weao.gg. И НИКОГДА НЕ СКАНИРУЙТЕ СЛУЧАЙНЫЕ QR-КОДЫ."
    ),
}

DEFAULT_SETTINGS = {
    "timeout_reason": "",
    "timeout_duration": 1440,
    "delete_window": 1440,
    "log_channel": 0,
    "auto_min_images": 4,
    "auto_min_channels": 2,
    "auto_window_seconds": 10,
}

DEFAULT_CONFIG = {
    "bot_lang": "en",
    "panel_lang": "en",
    "moderator_id": 0,
    "moderator_name": "",
}


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    for path in (DATA_DIR, IMAGES_DIR):
        try:
            os.chmod(path, 0o700)
        except OSError:
            pass


def write_bytes_atomic(path: Path, data: bytes):
    ensure_dirs()
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        try:
            os.chmod(tmp, 0o600)
        except OSError:
            pass
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_json(path: Path, data):
    write_bytes_atomic(path, json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))


def read_json(path: Path, default):
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except (OSError, ValueError) as e:
        logger.error(f"Cannot read {path.name}: {e}")
    return default


def effective_reason(settings: dict, lang: str) -> str:
    reason = settings.get("timeout_reason") or ""
    if not reason.strip() or reason in DEFAULT_REASON.values():
        reason = DEFAULT_REASON.get(lang, DEFAULT_REASON["en"])
    return reason[:MAX_REASON_LENGTH]


class GuildSettings:
    def __init__(self):
        self.data: dict[int, dict] = {}
        self.load()

    def load(self):
        raw = read_json(SETTINGS_FILE, {})
        data = {}
        if isinstance(raw, dict):
            for key, value in raw.items():
                try:
                    gid = int(key)
                except ValueError:
                    continue
                if isinstance(value, dict):
                    merged = DEFAULT_SETTINGS.copy()
                    merged.update({k: v for k, v in value.items() if k in DEFAULT_SETTINGS})
                    data[gid] = merged
        self.data = data
        logger.info(f"Settings loaded: {len(self.data)} guilds")

    def get(self, guild_id: int) -> dict:
        if guild_id not in self.data:
            self.data[guild_id] = DEFAULT_SETTINGS.copy()
        return self.data[guild_id]

    def save(self):
        try:
            write_json(SETTINGS_FILE, {str(k): v for k, v in self.data.items()})
        except OSError as e:
            logger.error(f"Save error: {e}")


class GlobalConfig:
    def __init__(self):
        self.data = DEFAULT_CONFIG.copy()
        raw = read_json(CONFIG_FILE, {})
        if isinstance(raw, dict):
            for key in DEFAULT_CONFIG:
                if key in raw:
                    self.data[key] = raw[key]
        for key in ("bot_lang", "panel_lang"):
            if self.data[key] not in LANGUAGES:
                self.data[key] = "en"

    @property
    def bot_lang(self) -> str:
        return self.data["bot_lang"]

    @property
    def panel_lang(self) -> str:
        return self.data["panel_lang"]

    @property
    def moderator_id(self) -> int:
        return int(self.data["moderator_id"] or 0)

    @property
    def moderator_name(self) -> str:
        return self.data["moderator_name"]

    def set_languages(self, bot_lang=None, panel_lang=None):
        if bot_lang in LANGUAGES:
            self.data["bot_lang"] = bot_lang
        if panel_lang in LANGUAGES:
            self.data["panel_lang"] = panel_lang
        self.save()

    def set_moderator(self, user_id: int, name: str):
        self.data["moderator_id"] = int(user_id)
        self.data["moderator_name"] = name
        self.save()

    def save(self):
        try:
            write_json(CONFIG_FILE, self.data)
        except OSError as e:
            logger.error(f"Config save error: {e}")
