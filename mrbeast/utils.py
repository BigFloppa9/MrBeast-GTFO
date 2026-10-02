import re
from datetime import timedelta

from .config import (
    MAX_DELETE_WINDOW_MINUTES,
    MAX_REASON_LENGTH,
    MAX_TIMEOUT_MINUTES,
)


def parse_duration(s: str) -> timedelta | None:
    total = 0
    for val, unit in re.findall(r"(\d+)([dhm])", (s or "").lower()):
        match unit:
            case "d": total += int(val) * 1440
            case "h": total += int(val) * 60
            case "m": total += int(val)
    return timedelta(minutes=total) if total > 0 else None


def fmt_duration(minutes: int) -> str:
    d, rem = divmod(int(minutes), 1440)
    h, m = divmod(rem, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    return " ".join(parts) or "0m"


def read_int(value, low: int, high: int):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if low <= number <= high else None


def apply_patch(s: dict, patch: dict) -> list[str]:
    new = {}
    errors = []

    if "timeout_reason" in patch:
        reason = patch["timeout_reason"]
        if not isinstance(reason, str):
            errors.append("reason_invalid")
        elif len(reason) > MAX_REASON_LENGTH:
            errors.append("reason_long")
        else:
            new["timeout_reason"] = reason.strip()

    if "timeout" in patch:
        td = parse_duration(str(patch["timeout"]))
        if td is None:
            errors.append("timeout_invalid")
        else:
            minutes = int(td.total_seconds() // 60)
            if minutes > MAX_TIMEOUT_MINUTES:
                errors.append("timeout_long")
            elif minutes < 1:
                errors.append("timeout_short")
            else:
                new["timeout_duration"] = minutes

    if "delete_window" in patch:
        td = parse_duration(str(patch["delete_window"]))
        if td is None:
            errors.append("delete_invalid")
        else:
            minutes = int(td.total_seconds() // 60)
            if minutes > MAX_DELETE_WINDOW_MINUTES:
                errors.append("delete_long")
            elif minutes < 1:
                errors.append("delete_short")
            else:
                new["delete_window"] = minutes

    for field, low, high in (
        ("auto_min_images", 1, 50),
        ("auto_min_channels", 1, 50),
        ("auto_window_seconds", 1, 3600),
    ):
        if field in patch:
            number = read_int(patch[field], low, high)
            if number is None:
                errors.append(f"{field}_range")
            else:
                new[field] = number

    if not errors:
        s.update(new)
    return errors
