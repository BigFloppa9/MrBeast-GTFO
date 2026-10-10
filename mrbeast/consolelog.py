import json
import logging
import threading
import time
from collections import deque

from .config import CONSOLE_FILE, write_bytes_atomic

MAX_LINES = 2000
MAX_AGE = 30 * 86400
COMPACT_EVERY = 500
LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}


class ConsoleLog(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.INFO)
        self.lock2 = threading.Lock()
        self.items: deque = deque(maxlen=MAX_LINES)
        self.session = time.time()
        self.activation = time.time()
        self.written = 0
        self.load()

    def load(self):
        cutoff = time.time() - MAX_AGE
        try:
            lines = CONSOLE_FILE.read_text(encoding="utf-8").splitlines()
        except OSError:
            return
        for line in lines[-MAX_LINES:]:
            try:
                item = json.loads(line)
            except ValueError:
                continue
            if isinstance(item, dict) and item.get("ts", 0) >= cutoff and "msg" in item:
                self.items.append(item)

    def emit(self, record: logging.LogRecord):
        try:
            message = record.getMessage()
            if record.exc_info:
                message += " | " + logging.Formatter().formatException(record.exc_info).splitlines()[-1]
        except Exception:
            return
        item = {"ts": round(record.created, 3), "level": record.levelname, "name": record.name, "msg": message[:1500]}
        with self.lock2:
            self.items.append(item)
            try:
                with open(CONSOLE_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
                try:
                    CONSOLE_FILE.chmod(0o600)
                except OSError:
                    pass
            except OSError:
                return
            self.written += 1
            if self.written >= COMPACT_EVERY:
                self.written = 0
                self.compact()

    def compact(self):
        payload = "".join(json.dumps(i, ensure_ascii=False) + "\n" for i in self.items).encode("utf-8")
        try:
            write_bytes_atomic(CONSOLE_FILE, payload)
        except OSError:
            pass

    def mark_activation(self):
        self.activation = time.time()

    def lines(self, limit: int = 100, since_activation: bool = False) -> list[dict]:
        with self.lock2:
            items = list(self.items)
        if since_activation:
            items = [i for i in items if i["ts"] >= self.activation]
        return items[-limit:] if limit else items

    def scrub(self, terms: set[str]) -> int:
        terms = {t.lower() for t in terms if t}
        if not terms:
            return 0
        with self.lock2:
            kept = [i for i in self.items if not any(t in i["msg"].lower() for t in terms)]
            removed = len(self.items) - len(kept)
            if removed:
                self.items = deque(kept, maxlen=MAX_LINES)
                self.compact()
        return removed


console = ConsoleLog()
