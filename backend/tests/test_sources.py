from .conftest import create_source


def test_source_and_propositions_have_stable_distinct_ids(client):
    response = create_source(client)

    assert response.status_code == 201
    source = response.json()
    assert source["id"] == "SRC-0001"
    assert [item["id"] for item in source["propositions"]] == [
        "SRC-0001/P01",
        "SRC-0001/P02",
    ]

    fetched = client.get("/api/v1/sources/SRC-0001")
    assert fetched.status_code == 200
    assert fetched.json() == source


def test_raw_archive_path_must_stay_below_external_data_root(client):
    payload = {
        "kind": "web_article",
        "original_url": "https://example.com/synthetic-source",
        "title": "合成来源示例",
        "raw_archive_path": "D:/emotion/private/article.txt",
    }

    response = client.post("/api/v1/sources", json=payload)

    assert response.status_code == 422


def test_raw_archive_path_is_normalized_as_a_relative_key(client):
    payload = {
        "kind": "web_article",
        "original_url": "https://example.com/synthetic-source",
        "title": "合成来源示例",
        "raw_archive_path": "raw\\sources\\SRC-TEST\\article.txt",
    }

    response = client.post("/api/v1/sources", json=payload)

    assert response.status_code == 201
    assert response.json()["raw_archive_path"] == (
        "raw/sources/SRC-TEST/article.txt"
    )
