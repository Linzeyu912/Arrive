from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings, prepare_data_directory, validate_database_url


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
        def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


settings = get_settings()
prepare_data_directory(settings.data_dir)
engine = build_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def create_schema(target_engine: Engine = engine) -> None:
    from . import models  # noqa: F401

    Base.metadata.create_all(target_engine)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
