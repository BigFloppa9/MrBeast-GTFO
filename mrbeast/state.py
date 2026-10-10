from .config import GlobalConfig, GuildSettings, ensure_dirs
from .logstore import LogStore
from .proxy import ProxyPool
from .strikes import StrikeStore
from .security import AuthStore, LoginLimiter, OneTimeCode, ResetFlow, Sessions


class State:
    def __init__(self):
        ensure_dirs()
        self.settings = GuildSettings()
        self.config = GlobalConfig()
        self.auth = AuthStore()
        self.logs = LogStore(self.auth.fernet)
        self.proxies = ProxyPool(self.auth.fernet)
        self.strikes = StrikeStore(self.auth.fernet)
        self.proxy_url = None
        self.sessions = Sessions()
        self.reg_code = OneTimeCode()
        self.reset = ResetFlow()
        self.limiter = LoginLimiter()
        self.runner = None
        self.update = {"running": False, "step": "", "error": "", "detail": ""}
        self.restart = False
        self.stop_event = None
        self.port = 0


state = State()
