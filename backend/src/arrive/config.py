from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo


_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DB_PATH = (_BACKEND_ROOT / "data" / "arrive.db").as_posix()


@dataclass(frozen=True)
class Settings:
    app_name: str = "ARRIVE API"
    api_prefix: str = "/api/v1"
    database_url: str = os.getenv(
        "ARRIVE_DATABASE_URL", f"sqlite:///{_DEFAULT_DB_PATH}"
    )
    default_timezone: str = os.getenv("ARRIVE_DEFAULT_TIMEZONE", "Asia/Shanghai")

    @property
    def timezone(self) -> ZoneInfo:
        return ZoneInfo(self.default_timezone)


@lru_cache
def get_settings() -> Settings:
    return Settings()
