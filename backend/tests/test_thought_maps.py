def test_thought_map_requires_edges_to_reference_known_nodes(client):
    invalid = client.post(
        "/api/v1/thought-maps",
        json={
            "title": "一张不完整的图",
            "nodes": [{"id": "P1", "type": "proposition", "text": "一个命题"}],
            "edges": [
                {"source": "P1", "target": "P2", "relation": "supports"}
            ],
        },
    )

    assert invalid.status_code == 422


def test_thought_map_preserves_contradictions(client):
    response = client.post(
        "/api/v1/thought-maps",
        json={
            "title": "关于独立与亲密",
            "version": "v0.1",
            "privacy": "private",
            "nodes": [
                {"id": "P1", "type": "proposition", "text": "我想保持独立"},
                {"id": "P2", "type": "proposition", "text": "我想被完全理解"},
            ],
            "edges": [
                {"source": "P1", "target": "P2", "relation": "contradicts"}
            ],
        },
    )

    assert response.status_code == 201
    thought_map = response.json()
    assert thought_map["id"] == "MAP-0001"
    assert thought_map["edges"][0]["relation"] == "contradicts"
