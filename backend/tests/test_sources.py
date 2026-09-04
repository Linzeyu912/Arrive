def create_source(client):
    return client.post(
        "/api/v1/sources",
        json={
            "kind": "web_article",
            "original_url": "https://example.com/love",
            "title": "什么时候适合谈恋爱",
            "platform": "示例平台",
            "language": "zh-CN",
            "topics": ["爱的能力", "关系修复"],
            "stance": "pending",
            "content_status": "mapped",
            "rights": "third_party_copyright",
            "propositions": [
                {
                    "text": "爱更应被理解为后天能力。",
                    "attribution": "collaborator_summary",
                },
                {
                    "text": "关系中的差异不必被消灭。",
                    "attribution": "collaborator_summary",
                },
            ],
        },
    )


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
