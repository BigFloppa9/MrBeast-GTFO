from .config import GlobalConfig, GuildSettings, ensure_dirs
from .logstore import LogStore
from .security import AuthStore, LoginLimiter, OneTimeCode, ResetFlow, Sessions


class State:
    def __init__(self):
        ensure_dirs()
        self.settings = GuildSettings()
        self.config = GlobalConfig()
        self.auth = AuthStore()
        self.logs = LogStore(self.auth.fernet)
        self.sessions = Sessions()
        self.reg_code = OneTimeCode()
        self.reset = ResetFlow()
        self.limiter = LoginLimiter()
        self.runner = None


state = State()
