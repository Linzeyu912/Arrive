import pytest

from arrive.config import Settings, prepare_data_directory, repository_root
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

    with pytest.raises(ValueError, match="inside the ARRIVE data directory"):
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
    (data_dir / "existing.txt").write_text("not ARRIVE data", encoding="utf-8")

    with pytest.raises(ValueError, match="non-empty directory without"):
        prepare_data_directory(data_dir)
