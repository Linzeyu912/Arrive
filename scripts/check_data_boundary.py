"""Fail when runtime/user data crosses into the ARRIVE software repository."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


FORBIDDEN_DIRECTORIES = (
    "content",
    "sources",
    "outputs",
    "data",
    "arrive-data",
    ".arrive-data",
    "backend/data",
    "runtime",
    "instance",
    "uploads",
    "logs",
    "cache",
    "backups",
    "manuscript",
    "exports",
    "attachments",
    "prompts",
    "model-runs",
    "embeddings",
    "backend/instance",
    "backend/uploads",
    "backend/logs",
    "backend/cache",
    "backend/exports",
    "backend/attachments",
)
FORBIDDEN_SUFFIXES = (
    ".db",
    ".db-journal",
    ".db-wal",
    ".db-shm",
    ".sqlite",
    ".sqlite3",
    ".sqlite-wal",
    ".sqlite-shm",
    ".log",
    ".dump",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
)
SQLITE_MAGIC = b"SQLite format 3\x00"
ALLOWED_TOP_LEVEL_DIRECTORIES = {
    ".githooks",
    ".github",
    "backend",
    "docs",
    "scripts",
    "templates",
}
ALLOWED_ROOT_FILES = {
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "SECURITY.md",
    "compose.yaml",
    "思考转译协作机制.md",
    "长文写作协作机制.md",
}
INSTANCE_ID_PATTERN = re.compile(
    r"^(?:id|source_id|event_id):\s*"
    r"(?:M\d{3}|M-\d{8}-\d{3}|P\d{3}|Q\d{3}|A\d{3}|X\d{3}|D\d{3}|"
    r"SRC-\d{4}|RSP-\d{8}-\d{3}|MAP-\d{4})\s*$",
    flags=re.MULTILINE,
)


def repository_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip()).resolve()


def tracked_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return [
        item.decode("utf-8", errors="surrogateescape").replace("\\", "/")
        for item in result.stdout.split(b"\0")
        if item
    ]


def is_forbidden_tracked_path(path: str) -> bool:
    normalized = path.casefold()
    name = normalized.rsplit("/", 1)[-1]
    if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
        return True
    if normalized.endswith(FORBIDDEN_SUFFIXES):
        return True
    return any(
        normalized == prefix.casefold()
        or normalized.startswith(f"{prefix.casefold()}/")
        for prefix in FORBIDDEN_DIRECTORIES
    )


def is_outside_software_layout(path: str) -> bool:
    parts = path.replace("\\", "/").split("/")
    if len(parts) == 1:
        return parts[0] not in ALLOWED_ROOT_FILES
    return parts[0] not in ALLOWED_TOP_LEVEL_DIRECTORIES


def indexed_blob(root: Path, path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f":{path}"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    return result.stdout if result.returncode == 0 else b""


def contains_sqlite_database(content: bytes) -> bool:
    return content.startswith(SQLITE_MAGIC)


def contains_instance_frontmatter(path: str, content: bytes) -> bool:
    normalized = path.casefold()
    if normalized.startswith("templates/"):
        return False
    if not normalized.endswith((".md", ".yaml", ".yml")):
        return False

    text = content.decode("utf-8-sig", errors="replace")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    try:
        closing_index = next(
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        )
    except StopIteration:
        return False
    frontmatter = "\n".join(lines[1:closing_index])
    return INSTANCE_ID_PATTERN.search(frontmatter) is not None


def is_inside(path: Path, root: Path) -> bool:
    path = path.expanduser().resolve(strict=False)
    root = root.expanduser().resolve(strict=False)
    return path == root or root in path.parents


def main() -> int:
    root = repository_root()
    tracked = tracked_paths(root)
    indexed_content = {path: indexed_blob(root, path) for path in tracked}
    tracked_violations = [
        path for path in tracked if is_forbidden_tracked_path(path)
    ]
    layout_violations = [
        path
        for path in tracked
        if path not in tracked_violations and is_outside_software_layout(path)
    ]
    disguised_databases = [
        path
        for path in tracked
        if path not in tracked_violations
        and contains_sqlite_database(indexed_content[path])
    ]
    instance_records = [
        path
        for path in tracked
        if path not in tracked_violations
        and contains_instance_frontmatter(path, indexed_content[path])
    ]
    local_violations = [
        relative
        for relative in FORBIDDEN_DIRECTORIES
        if (root / relative).exists() or (root / relative).is_symlink()
    ]

    configured_data_dir = os.getenv("ARRIVE_DATA_DIR")
    configured_violation = bool(
        configured_data_dir
        and (
            is_inside(Path(configured_data_dir), root)
            or is_inside(root, Path(configured_data_dir))
        )
    )

    if (
        not tracked_violations
        and not layout_violations
        and not disguised_databases
        and not instance_records
        and not local_violations
        and not configured_violation
    ):
        print("ARRIVE data boundary check passed.")
        return 0

    print("ARRIVE data boundary check failed.", file=sys.stderr)
    if tracked_violations:
        print("Tracked runtime/data paths:", file=sys.stderr)
        for path in tracked_violations:
            print(f"  - {path}", file=sys.stderr)
    if layout_violations:
        print("Tracked paths outside the software allowlist:", file=sys.stderr)
        for path in layout_violations:
            print(f"  - {path}", file=sys.stderr)
    if disguised_databases:
        print("Tracked files containing a SQLite database:", file=sys.stderr)
        for path in disguised_databases:
            print(f"  - {path}", file=sys.stderr)
    if instance_records:
        print("Tracked files that look like ARRIVE instance records:", file=sys.stderr)
        for path in instance_records:
            print(f"  - {path}", file=sys.stderr)
    if local_violations:
        print("Runtime/data directories inside the repository:", file=sys.stderr)
        for path in local_violations:
            print(f"  - {path}/", file=sys.stderr)
    if configured_violation:
        print(
            "ARRIVE_DATA_DIR overlaps the software repository: "
            f"{Path(configured_data_dir).resolve(strict=False)}",
            file=sys.stderr,
        )
    print(
        "Move these items to an external ARRIVE_DATA_DIR before committing.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
