from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import Connection, Engine, create_engine, event, inspect
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings, prepare_data_directory, validate_database_url

if TYPE_CHECKING:
    from alembic.script import ScriptDirectory


class Base(DeclarativeBase):
    pass


def build_engine(database_url: str) -> Engine:
    url = make_url(database_url)
    database_path = validate_database_url(database_url)
    connect_args: dict[str, object] = {}

    if url.get_backend_name() == "sqlite":
        connect_args["check_same_thread"] = False
        if database_path is not None:
            database_path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(database_url, connect_args=connect_args)

    if url.get_backend_name() == "sqlite":

        @event.listens_for(engine, "connect")
        def _configure_sqlite_connection(
            dbapi_connection, _connection_record
        ) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()

    return engine


settings = get_settings()
prepare_data_directory(settings.data_dir)
engine = build_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _migrations_dir() -> Path:
    # A repository checkout (editable install) keeps migrations next to the
    # package; a container image installs the package and copies migrations
    # to the working directory.
    candidates = [
        Path(__file__).resolve().parents[2] / "migrations",
        Path.cwd() / "migrations",
    ]
    for candidate in candidates:
        if (candidate / "env.py").is_file():
            return candidate
    raise FileNotFoundError(
        "could not locate the Alembic migrations directory; expected it "
        "next to the backend package or in the working directory"
    )


def _legacy_bootstrap_revision(
    connection: Connection, script: "ScriptDirectory"
) -> str | None:
    """Stamp revision for databases created by the retired create_all path.

    Such databases carry tables but no alembic_version row. A create_all
    database always matched the metadata of the code that built it, so the
    response-events composite index distinguishes the current schema from
    the initial one.
    """
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    if not tables or "alembic_version" in tables:
        return None
    if "response_events" in tables:
        index_names = {
            index["name"] for index in inspector.get_indexes("response_events")
        }
        if "ix_response_events_target_effective" in index_names:
            return script.get_current_head()
    return script.get_base()


def run_migrations(database_url: str | None = None) -> None:
    """Bring the schema to the latest Alembic revision.

    Migrations are the single source of the schema: application startup and
    the test suite both go through this function instead of create_all.
    """
    from alembic import command
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    config = Config()
    config.set_main_option("script_location", str(_migrations_dir()))
    if database_url is not None:
        config.set_main_option("sqlalchemy.url", database_url)

    script = ScriptDirectory.from_config(config)

    with build_engine(
        database_url if database_url is not None else settings.database_url
    ).connect() as connection:
        legacy_revision = _legacy_bootstrap_revision(connection, script)
    if legacy_revision is not None:
        command.stamp(config, legacy_revision)

    command.upgrade(config, "head")


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
