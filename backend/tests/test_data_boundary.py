import os
import subprocess

import pytest

from arrive.config import (
    DATA_SUBDIRECTORIES, Settings, data_path, prepare_data_directory, repository_root,
    require_data_boundary,
)
from arrive.database import build_engine


def test_default_database_is_derived_from_external_data_directory(
    monkeypatch, tmp_path
):
    data_dir = tmp_path / "arrive-data"
    monkeypatch.setenv("ARRIVE_DATA_DIR", str(data_dir))
    monkeypatch.delenv("ARRIVE_DATABASE_URL", raising=False)

    settings = Settings()

    assert settings.data_dir == data_dir.resolve()
    assert settings.database_url == (
        f"sqlite:///{(data_dir / 'database' / 'arrive.db').as_posix()}"
    )


def test_data_directory_inside_repository_is_rejected():
    with pytest.raises(ValueError, match="physically separate"):
        Settings(
            data_dir=repository_root() / "content",
            database_url="sqlite:///:memory:",
        )


def test_data_directory_cannot_contain_repository():
    with pytest.raises(ValueError, match="physically separate"):
        Settings(
            data_dir=repository_root().parent,
            database_url="sqlite:///:memory:",
        )


def test_configured_sqlite_must_be_inside_data_directory(tmp_path):
    data_dir = tmp_path / "data-root"
    database_path = tmp_path / "other" / "arrive.db"

    with pytest.raises(ValueError, match="inside the Arrive data directory"):
        Settings(
            data_dir=data_dir,
            database_url=f"sqlite:///{database_path.as_posix()}",
        )


def test_sqlite_database_inside_repository_is_rejected(tmp_path):
    forbidden_path = repository_root() / "backend" / "data" / "forbidden.db"

    with pytest.raises(ValueError, match="SQLite database must be physically separate"):
        build_engine(f"sqlite:///{forbidden_path.as_posix()}")

    assert not forbidden_path.exists()


def test_external_sqlite_database_is_allowed(tmp_path):
    database_path = tmp_path / "database" / "allowed.db"

    engine = build_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        with engine.connect():
            pass
    finally:
        engine.dispose()

    assert database_path.is_file()


def test_empty_external_data_directory_is_marked(tmp_path):
    data_dir = tmp_path / "new-data-root"

    result = prepare_data_directory(data_dir)

    assert result == data_dir.resolve()
    assert (data_dir / ".arrive-data-root").read_text(encoding="utf-8") == (
        "ARRIVE_DATA_ROOT_V1\n"
    )


def test_nonempty_unmarked_directory_is_rejected(tmp_path):
    data_dir = tmp_path / "unrelated"
    data_dir.mkdir()
    (data_dir / "existing.txt").write_text("not Arrive data", encoding="utf-8")

    with pytest.raises(ValueError, match="non-empty directory without"):
        prepare_data_directory(data_dir)


def test_default_without_environment_uses_ignored_project_data(monkeypatch):
    monkeypatch.delenv("ARRIVE_DATA_DIR", raising=False)
    monkeypatch.delenv("ARRIVE_DATABASE_URL", raising=False)
    settings = Settings()
    assert settings.data_dir == repository_root() / "arrive-data"


def test_project_data_requires_ignore_and_rejects_force_tracked_files(tmp_path):
    repo = tmp_path / "synthetic-repository"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    data = repo / "arrive-data"
    with pytest.raises(ValueError, match="Git-ignored and untracked"):
        require_data_boundary(data, label="test", repository_root=repo)
    (repo / ".gitignore").write_text("/arrive-data/\n", encoding="utf-8")
    assert require_data_boundary(data, label="test", repository_root=repo) == data
    data.mkdir()
    (data / "synthetic.txt").write_text("Completely fictional test data", encoding="utf-8")
    subprocess.run(
        ["git", "add", "-f", "arrive-data/synthetic.txt"],
        cwd=repo, check=True, capture_output=True,
    )
    with pytest.raises(ValueError, match="Git-ignored and untracked"):
        require_data_boundary(data, label="test", repository_root=repo)


def test_boundary_check_allows_ignored_data_but_rejects_tracked_data(tmp_path, monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "boundary_check", repository_root() / "scripts" / "check_data_boundary.py"
    )
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    repo = tmp_path / "synthetic-repository"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    (repo / ".gitignore").write_text("/arrive-data/\n", encoding="utf-8")
    data = repo / "arrive-data"
    data.mkdir()
    (data / "synthetic.txt").write_text("Completely fictional test data", encoding="utf-8")
    monkeypatch.chdir(repo)
    monkeypatch.setenv("ARRIVE_DATA_DIR", str(data))
    assert checker.main() == 0
    subprocess.run(["git", "add", "-f", "arrive-data/synthetic.txt"], check=True, capture_output=True)
    assert checker.main() == 1


def test_initialization_creates_all_runtime_locations_and_ignore(tmp_path):
    root = prepare_data_directory(tmp_path / "private")
    assert "*" in (root / ".gitignore").read_text().splitlines()
    assert all((root / name).is_dir() for name in DATA_SUBDIRECTORIES)
    # Reopening a marked root preserves existing synthetic data.
    item = data_path(root, "outputs/synthetic.txt")
    item.write_text("synthetic test output", encoding="utf-8")
    prepare_data_directory(root)
    assert item.read_text(encoding="utf-8") == "synthetic test output"


def test_database_cannot_be_placed_in_output_directory(tmp_path):
    root = tmp_path / "private"
    with pytest.raises(ValueError, match="ARRIVE_DATA_DIR/database"):
        Settings(data_dir=root, database_url=f"sqlite:///{root.as_posix()}/outputs/db.sqlite")


@pytest.mark.parametrize("key", [
    "../outside", "outputs/../../outside", "/outputs/a", "C:/outputs/a",
    "C:outputs/a", "outputs/a:stream", "docs/research/a", "",
])
def test_unsafe_runtime_keys_are_rejected(tmp_path, key):
    with pytest.raises(ValueError):
        data_path(tmp_path / "private", key)


@pytest.mark.parametrize("url", [
    "sqlite:///file:outside.db?uri=true",
    "sqlite:///file::memory:?cache=shared&uri=true",
])
def test_sqlite_uri_paths_are_rejected(tmp_path, url):
    with pytest.raises(ValueError, match="URI filenames"):
        Settings(data_dir=tmp_path / "private", database_url=url)


def test_data_directory_in_another_git_tree_is_rejected(tmp_path):
    (tmp_path / ".git").mkdir()
    with pytest.raises(ValueError, match="Git working tree"):
        prepare_data_directory(tmp_path / "private")


def test_linked_runtime_directory_cannot_escape(tmp_path):
    root = prepare_data_directory(tmp_path / "private")
    outside = tmp_path / "outside"
    outside.mkdir()
    link = root / "outputs" / "linked"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        if os.name != "nt":
            pytest.skip("Creating symlinks requires OS privileges")
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(outside)],
            check=True, capture_output=True,
        )
    try:
        with pytest.raises(ValueError, match="escapes"):
            data_path(root, "outputs/linked/synthetic.txt")
    finally:
        if link.is_symlink():
            link.unlink()
        else:
            # Remove the junction itself, never recurse into its target.
            link.rmdir()
