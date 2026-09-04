from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy.engine import make_url


_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_REPOSITORY_ROOT = _BACKEND_ROOT.parent
_DEFAULT_DATA_DIR = _REPOSITORY_ROOT.parent / "arrive-data"
_DATA_ROOT_MARKER = ".arrive-data-root"
_DATA_ROOT_MARKER_VALUE = "ARRIVE_DATA_ROOT_V1"


def _resolved(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def _is_inside(candidate: Path, container: Path) -> bool:
    candidate = _resolved(candidate)
    container = _resolved(container)
    return candidate == container or container in candidate.parents


def require_outside_repository(
    path: Path,
    *,
    label: str,
    repository_root: Path = _REPOSITORY_ROOT,
) -> Path:
    resolved = _resolved(path)
    if _is_inside(resolved, repository_root) or _is_inside(
        repository_root, resolved
    ):
        raise ValueError(
            f"{label} must be physically separate from the software repository: "
            f"{resolved}"
        )
    return resolved


def sqlite_database_path(database_url: str) -> Path | None:
    url = make_url(database_url)
    if url.get_backend_name() != "sqlite" or not url.database:
        return None
    if url.database == ":memory:":
        return None

    path = Path(url.database).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return _resolved(path)


def validate_database_url(
    database_url: str,
    *,
    repository_root: Path = _REPOSITORY_ROOT,
) -> Path | None:
    database_path = sqlite_database_path(database_url)
    if database_path is not None:
        require_outside_repository(
            database_path,
            label="SQLite database",
            repository_root=repository_root,
        )
    return database_path


def repository_root() -> Path:
    return _REPOSITORY_ROOT


def prepare_data_directory(data_dir: Path) -> Path:
    resolved = require_outside_repository(
        data_dir,
        label="Arrive data directory",
    )
    if resolved.exists() and not resolved.is_dir():
        raise ValueError(f"Arrive data directory is not a directory: {resolved}")

    marker = resolved / _DATA_ROOT_MARKER
    if marker.exists():
        if marker.read_text(encoding="utf-8").strip() != _DATA_ROOT_MARKER_VALUE:
            raise ValueError(f"Invalid Arrive data-root marker: {marker}")
        return resolved

    if resolved.exists() and any(resolved.iterdir()):
        raise ValueError(
            "Refusing to use a non-empty directory without an Arrive "
            f"data-root marker: {resolved}"
        )

    resolved.mkdir(parents=True, exist_ok=True)
    marker.write_text(f"{_DATA_ROOT_MARKER_VALUE}\n", encoding="utf-8")
    return resolved


@dataclass(frozen=True)
class Settings:
    app_name: str = "Arrive API"
    api_prefix: str = "/api/v1"
    data_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv("ARRIVE_DATA_DIR", str(_DEFAULT_DATA_DIR))
        )
    )
    database_url: str = field(
        default_factory=lambda: os.getenv("ARRIVE_DATABASE_URL", "")
    )
    default_timezone: str = field(
        default_factory=lambda: os.getenv(
            "ARRIVE_DEFAULT_TIMEZONE", "Asia/Shanghai"
        )
    )

    def __post_init__(self) -> None:
        data_dir = require_outside_repository(
            self.data_dir,
            label="Arrive data directory",
        )
        database_url = self.database_url or (
            f"sqlite:///{(data_dir / 'database' / 'arrive.db').as_posix()}"
        )
        database_path = validate_database_url(database_url)
        if database_path is not None and not _is_inside(database_path, data_dir):
            raise ValueError(
                "SQLite database must be inside the Arrive data directory: "
                f"{database_path}"
            )

        object.__setattr__(self, "data_dir", data_dir)
        object.__setattr__(self, "database_url", database_url)

    @property
    def timezone(self) -> ZoneInfo:
        return ZoneInfo(self.default_timezone)


@lru_cache
def get_settings() -> Settings:
    return Settings()
