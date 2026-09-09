import sqlite3
from pathlib import Path

from sqlalchemy import create_engine

from arrive.database import Base, run_migrations
from arrive import models  # noqa: F401


def _migrations_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "migrations"


def _head_revision() -> str:
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    config = Config()
    config.set_main_option("script_location", str(_migrations_dir()))
    return ScriptDirectory.from_config(config).get_current_head()


def _response_event_indexes(database: Path) -> set[str]:
    connection = sqlite3.connect(database)
    try:
        rows = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='index' AND tbl_name='response_events'"
        ).fetchall()
    finally:
        connection.close()
    return {row[0] for row in rows}


def test_fresh_database_is_created_purely_by_migrations(tmp_path):
    database = tmp_path / "fresh.db"

    run_migrations(f"sqlite:///{database.as_posix()}")

    connection = sqlite3.connect(database)
    try:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        version = connection.execute(
            "SELECT version_num FROM alembic_version"
        ).fetchone()[0]
    finally:
        connection.close()

    assert "alembic_version" in tables
    assert {
        "materials",
        "sources",
        "source_propositions",
        "personal_propositions",
        "response_events",
        "thought_maps",
    } <= tables
    assert version == _head_revision()
    assert "ix_response_events_target_effective" in _response_event_indexes(database)


def test_create_all_era_database_at_current_schema_is_stamped_at_head(tmp_path):
    database = tmp_path / "legacy-current.db"
    url = f"sqlite:///{database.as_posix()}"

    legacy_engine = create_engine(url)
    Base.metadata.create_all(legacy_engine, tables=[t for t in Base.metadata.sorted_tables if t.name not in {"legacy_documents", "document_jobs"}])
    legacy_engine.dispose()

    run_migrations(url)

    connection = sqlite3.connect(database)
    try:
        version = connection.execute(
            "SELECT version_num FROM alembic_version"
        ).fetchone()[0]
    finally:
        connection.close()

    assert version == _head_revision()
    assert "ix_response_events_target_effective" in _response_event_indexes(database)


def test_create_all_era_database_at_initial_schema_is_stamped_and_upgraded(tmp_path):
    database = tmp_path / "legacy-initial.db"
    url = f"sqlite:///{database.as_posix()}"

    legacy_engine = create_engine(url)
    Base.metadata.create_all(legacy_engine, tables=[t for t in Base.metadata.sorted_tables if t.name not in {"legacy_documents", "document_jobs"}])
    legacy_engine.dispose()

    connection = sqlite3.connect(database)
    connection.execute("DROP INDEX ix_response_events_target_effective")
    connection.execute(
        "CREATE INDEX ix_response_events_target_id ON response_events (target_id)"
    )
    connection.commit()
    connection.close()

    run_migrations(url)

    connection = sqlite3.connect(database)
    try:
        version = connection.execute(
            "SELECT version_num FROM alembic_version"
        ).fetchone()[0]
    finally:
        connection.close()

    indexes = _response_event_indexes(database)
    assert version == _head_revision()
    assert "ix_response_events_target_effective" in indexes
    assert "ix_response_events_target_id" not in indexes

def test_upgrade_preserves_sources_and_attribution(tmp_path):
    from alembic import command
    from alembic.config import Config
    from sqlalchemy.orm import Session
    from arrive.schemas import SourceCreate
    database = tmp_path / 'with-source.db'
    url = f'sqlite:///{database.as_posix()}'
    config = Config()
    config.set_main_option('script_location', str(_migrations_dir()))
    config.set_main_option('sqlalchemy.url', url)
    command.upgrade(config, 'b72e9104c301')
    engine = create_engine(url)
    payload = SourceCreate(kind='web_article', original_url='https://example.org/synthetic', title='Synthetic migration source')
    fields=payload.model_dump(exclude={'propositions'})
    fields['original_url']=str(payload.original_url)
    with Session(engine) as session:
        source=models.Source(public_id='SRC-9000', created_at='2026-09-09T12:00:00+08:00', **fields)
        source.propositions.append(models.SourceProposition(public_id='SRC-9000/P01',ordinal=1,text='Synthetic proposition.',attribution='author_explicit',created_at='2026-09-09T12:00:00+08:00'))
        session.add(source)
        session.commit()
    engine.dispose()
    run_migrations(url)
    with sqlite3.connect(database) as connection:
        assert connection.execute('SELECT title FROM sources').fetchone()[0]=='Synthetic migration source'
        assert connection.execute('SELECT public_id FROM source_propositions').fetchone()[0]=='SRC-9000/P01'
        assert not connection.execute('PRAGMA foreign_key_check').fetchall()
        assert connection.execute('SELECT count(*) FROM document_jobs').fetchone()[0]==0
