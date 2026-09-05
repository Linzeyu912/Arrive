from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path, PurePosixPath, PureWindowsPath
from zoneinfo import ZoneInfo

from sqlalchemy.engine import make_url


_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_REPOSITORY_ROOT = _BACKEND_ROOT.parent
_DEFAULT_DATA_DIR = _REPOSITORY_ROOT.parent / "arrive-data"
_DATA_ROOT_MARKER = ".arrive-data-root"
_DATA_ROOT_MARKER_VALUE = "ARRIVE_DATA_ROOT_V1"
DATA_SUBDIRECTORIES = (
    "database", "raw", "inbox", "materials", "sources", "mirrors",
    "semantics", "responses", "thought-maps", "drafts", "decisions",
    "outputs", "exports", "model-runs", "logs", "cache", "embeddings",
    "backups",
)


def data_path(data_dir: Path, key: str) -> Path:
    """Resolve a runtime storage key without allowing traversal or link escape.

    Future file writers must call this immediately before accessing a path.
    This is configuration safety, not protection against concurrent local
    filesystem tampering by another process.
    """
    normalized = key.replace("\\", "/")
    parts = PurePosixPath(normalized).parts
    if (
        not parts or PureWindowsPath(key).drive
        or normalized.startswith("/") or ".." in parts
        or ":" in normalized or "\x00" in normalized
        or parts[0] not in DATA_SUBDIRECTORIES
    ):
        raise ValueError("Invalid Arrive data storage key")
    root = require_outside_repository(data_dir, label="Arrive data directory")
    target = _resolved(root.joinpath(*parts))
    if not _is_inside(target, root):
        raise ValueError("Data storage key escapes the Arrive data directory")
    require_outside_repository(target, label="Arrive data file")
    return target


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
    if url.get_backend_name() == "sqlite" and (
        url.query.get("uri") is not None
        or (url.database or "").startswith("file:")
    ):
        raise ValueError("SQLite URI filenames are not supported; use a plain file path")
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
    if any((parent / ".git").exists() for parent in (resolved, *resolved.parents)):
        raise ValueError("Arrive data directory must not be in a Git working tree")
    if marker.is_symlink():
        raise ValueError("Arrive data-root marker must not be a symbolic link")
    if marker.exists():
        if marker.read_text(encoding="utf-8").strip() != _DATA_ROOT_MARKER_VALUE:
            raise ValueError(f"Invalid Arrive data-root marker: {marker}")
    elif resolved.exists() and any(resolved.iterdir()):
        raise ValueError(
            "Refusing to use a non-empty directory without an Arrive "
            f"data-root marker: {resolved}"
        )

    # Validate every managed location before creating anything in an existing root.
    locations = [data_path(resolved, name) for name in DATA_SUBDIRECTORIES]
    if any(path.exists() and not path.is_dir() for path in locations):
        raise ValueError("An Arrive data subdirectory is occupied by a file")
    ignore = resolved / ".gitignore"
    if ignore.is_symlink():
        raise ValueError("Arrive data .gitignore must not be a symbolic link")
    resolved.mkdir(parents=True, exist_ok=True)
    if not marker.exists():
        marker.write_text(f"{_DATA_ROOT_MARKER_VALUE}\n", encoding="utf-8")
    if not ignore.exists():
        ignore.write_text("# Private Arrive runtime data: never commit.\n*\n", encoding="utf-8")
    for location in locations:
        location.mkdir(parents=True, exist_ok=True)
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
        if database_path is not None:
            database_dir = data_path(data_dir, "database")
            if database_path == database_dir or not _is_inside(database_path, database_dir):
                raise ValueError("SQLite database must be inside ARRIVE_DATA_DIR/database")

        object.__setattr__(self, "data_dir", data_dir)
        object.__setattr__(self, "database_url", database_url)

    @property
    def timezone(self) -> ZoneInfo:
        return ZoneInfo(self.default_timezone)


@lru_cache
def get_settings() -> Settings:
    return Settings()
