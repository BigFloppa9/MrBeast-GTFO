import json
import logging
import os
import secrets
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
STRIKES_FILE = DATA_DIR / "strikes.json"
CONSOLE_FILE = DATA_DIR / "console.log"
BIN_DIR = DATA_DIR / "bin"
XRAY_DIR = DATA_DIR / "xray"
CACHE_DIR = DATA_DIR / "cache"

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

MAX_STEPS = 8
MAX_MODERATORS = 10
MAX_BAN_DELETE_MINUTES = 7 * 1440
RETENTION_DAYS = 90
PRESETS = ("default", "ladder", "ladder_ban", "custom")

DEFAULT_SETTINGS = {
    "timeout_reason": "",
    "timeout_duration": 1440,
    "delete_window": 1440,
    "log_channel": 0,
    "auto_min_images": 4,
    "auto_min_channels": 2,
    "auto_window_seconds": 10,
    "punish_preset": "default",
    "custom_steps": [],
    "warn_reset_days": 30,
    "dm_reason": True,
}

APPEAL_NOTE = {
    "en": "If this moderation was a mistake, please contact a server moderator.",
    "ru": "Если модерация оказалась ошибочной, свяжитесь с модератором сервера.",
}
STEP_NOTE = {
    "en": "Detection {n} of {total}.",
    "ru": "Обнаружение {n} из {total}.",
}


def ladder_steps(preset: str) -> list[dict]:
    if preset == "ladder":
        return [
            {"action": "timeout", "duration": 5, "delete": 60},
            {"action": "timeout", "duration": 1440, "delete": 1440},
            {"action": "timeout", "duration": 10080, "delete": 1440},
            {"action": "ban", "duration": 0, "delete": 1440},
        ]
    if preset == "ladder_ban":
        return [{"action": "ban", "duration": 0, "delete": 1440}]
    return []


def clean_step(raw) -> dict | None:
    if not isinstance(raw, dict):
        return None
    action = raw.get("action")
    if action not in ("timeout", "ban"):
        return None
    try:
        duration = int(raw.get("duration") or 0)
        delete = int(raw.get("delete") or 0)
    except (TypeError, ValueError):
        return None
    reason = raw.get("reason")
    reason = reason.strip()[:MAX_REASON_LENGTH] if isinstance(reason, str) else ""
    if action == "timeout" and not 1 <= duration <= MAX_TIMEOUT_MINUTES:
        return None
    if not 0 <= delete <= (MAX_BAN_DELETE_MINUTES if action == "ban" else MAX_DELETE_WINDOW_MINUTES):
        return None
    return {"action": action, "duration": duration if action == "timeout" else 0, "delete": delete, "reason": reason}


def steps_for(settings: dict) -> list[dict]:
    preset = settings.get("punish_preset", "default")
    if preset == "custom":
        steps = [clean_step(s) for s in settings.get("custom_steps") or []]
        steps = [s for s in steps if s]
        if steps:
            return steps[:MAX_STEPS]
    elif preset in ("ladder", "ladder_ban"):
        return [dict(s, reason="") for s in ladder_steps(preset)]
    return [{"action": "timeout", "duration": settings["timeout_duration"], "delete": settings["delete_window"], "reason": settings.get("timeout_reason") or ""}]


def step_reason(settings: dict, index: int, total: int, lang: str) -> str:
    steps = steps_for(settings)
    step = steps[min(index, len(steps) - 1)]
    reason = (step.get("reason") or "").strip()
    preset = settings.get("punish_preset", "default")
    if not reason or reason in DEFAULT_REASON.values():
        reason = DEFAULT_REASON.get(lang, DEFAULT_REASON["en"])
        if preset == "ladder":
            reason = f"{STEP_NOTE.get(lang, STEP_NOTE['en']).format(n=index + 1, total=total)} {reason} {APPEAL_NOTE.get(lang, APPEAL_NOTE['en'])}"
    return reason

DEFAULT_CONFIG = {
    "bot_lang": "en",
    "panel_lang": "en",
    "moderator_id": 0,
    "moderator_name": "",
    "moderators": [],
    "bot_state": "running",
    "hwid": "",
}


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for path in (DATA_DIR, IMAGES_DIR, CACHE_DIR):
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
    return reason


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
                    merged["custom_steps"] = []
                    merged.update({k: v for k, v in value.items() if k in DEFAULT_SETTINGS})
                    if merged["punish_preset"] not in PRESETS:
                        merged["punish_preset"] = "default"
                    data[gid] = merged
        self.data = data
        logger.info(f"Settings loaded: {len(self.data)} guilds")

    def get(self, guild_id: int) -> dict:
        if guild_id not in self.data:
            self.data[guild_id] = dict(DEFAULT_SETTINGS, custom_steps=[])
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
        if self.data["bot_state"] not in ("running", "paused", "stopped"):
            self.data["bot_state"] = "running"
        mods = self.data.get("moderators")
        if not isinstance(mods, list):
            mods = []
        mods = [m for m in mods if isinstance(m, dict) and str(m.get("id", "")).isdigit()]
        if not mods and self.data.get("moderator_id"):
            mods = [{"id": int(self.data["moderator_id"]), "name": str(self.data.get("moderator_name") or "")}]
        self.data["moderators"] = mods[:MAX_MODERATORS]
        if not isinstance(self.data.get("hwid"), str) or not self.data["hwid"]:
            self.data["hwid"] = secrets.token_hex(8)
            self.save()

    @property
    def bot_lang(self) -> str:
        return self.data["bot_lang"]

    @property
    def panel_lang(self) -> str:
        return self.data["panel_lang"]

    @property
    def bot_state(self) -> str:
        return self.data["bot_state"]

    def set_bot_state(self, value: str):
        self.data["bot_state"] = value
        self.save()

    @property
    def moderators(self) -> list[dict]:
        return self.data["moderators"]

    @property
    def hwid(self) -> str:
        return self.data["hwid"]

    def is_moderator(self, user_id: int) -> bool:
        return any(int(m["id"]) == int(user_id) for m in self.moderators)

    def set_languages(self, bot_lang=None, panel_lang=None):
        if bot_lang in LANGUAGES:
            self.data["bot_lang"] = bot_lang
        if panel_lang in LANGUAGES:
            self.data["panel_lang"] = panel_lang
        self.save()

    def add_moderator(self, user_id: int, name: str) -> bool:
        mods = [m for m in self.moderators if int(m["id"]) != int(user_id)]
        if len(mods) >= MAX_MODERATORS:
            return False
        mods.append({"id": int(user_id), "name": name})
        self.data["moderators"] = mods
        self.data["moderator_id"], self.data["moderator_name"] = 0, ""
        self.save()
        return True

    def remove_moderator(self, user_id: int) -> bool:
        mods = [m for m in self.moderators if int(m["id"]) != int(user_id)]
        if len(mods) == len(self.moderators):
            return False
        self.data["moderators"] = mods
        self.save()
        return True

    def save(self):
        try:
            write_json(CONFIG_FILE, self.data)
        except OSError as e:
            logger.error(f"Config save error: {e}")
