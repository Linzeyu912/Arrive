from __future__ import annotations

from datetime import datetime, timezone

from .config import get_settings


def now_in_default_timezone() -> datetime:
    return datetime.now(get_settings().timezone).replace(microsecond=0)


def require_aware(value: datetime, field_name: str = "timestamp") -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone offset")
    return value


def truncated_to_seconds(value: datetime) -> datetime:
    return require_aware(value).replace(microsecond=0)


def exact_iso(value: datetime) -> str:
    return truncated_to_seconds(value).isoformat(timespec="seconds")


def epoch_ms(value: datetime) -> int:
    aware = require_aware(value)
    return int(aware.astimezone(timezone.utc).timestamp() * 1000)


def dual_time(value: datetime) -> tuple[str, int]:
    """Second-level ISO string and UTC epoch milliseconds for one instant.

    Both stored columns are derived from the same second-truncated datetime so
    they can never disagree about sub-second precision.
    """
    truncated = truncated_to_seconds(value)
    return (
        truncated.isoformat(timespec="seconds"),
        int(truncated.astimezone(timezone.utc).timestamp() * 1000),
    )
