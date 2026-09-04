from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from arrive.database import build_engine, create_schema, get_session
from arrive.main import create_app


@pytest.fixture
def client(tmp_path) -> Generator[TestClient, None, None]:
    database_path = (tmp_path / "test.db").as_posix()
    test_engine = build_engine(f"sqlite:///{database_path}")
    create_schema(test_engine)
    testing_session = sessionmaker(
        bind=test_engine, autoflush=False, expire_on_commit=False
    )

    def override_session() -> Generator[Session, None, None]:
        with testing_session() as session:
            yield session

    app = create_app(initialize_database=False)
    app.dependency_overrides[get_session] = override_session

    with TestClient(app) as test_client:
        yield test_client

    test_engine.dispose()
