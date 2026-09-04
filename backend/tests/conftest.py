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


def create_source(client):
    return client.post(
        "/api/v1/sources",
        json={
            "kind": "web_article",
            "original_url": "https://example.com/synthetic-source",
            "title": "合成来源示例",
            "platform": "示例平台",
            "language": "zh-CN",
            "topics": ["表达", "协作"],
            "stance": "pending",
            "content_status": "mapped",
            "rights": "third_party_copyright",
            "propositions": [
                {
                    "text": "表达前应明确接收者。",
                    "attribution": "collaborator_summary",
                },
                {
                    "text": "复杂性不应被自动消除。",
                    "attribution": "collaborator_summary",
                },
            ],
        },
    )
