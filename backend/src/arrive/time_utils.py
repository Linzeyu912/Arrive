from __future__ import annotations

from datetime import datetime, timezone

from .config import get_settings


def now_in_default_timezone() -> datetime:
    return datetime.now(get_settings().timezone).replace(microsecond=0)


def require_aware(value: datetime, field_name: str = "timestamp") -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone offset")
    return value


def exact_iso(value: datetime) -> str:
    return require_aware(value).isoformat(timespec="seconds")


def epoch_ms(value: datetime) -> int:
    aware = require_aware(value)
    return int(aware.astimezone(timezone.utc).timestamp() * 1000)
