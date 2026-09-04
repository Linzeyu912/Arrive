def test_material_preserves_exact_words_and_time(client):
    response = client.post(
        "/api/v1/materials",
        json={
            "kind": "contradiction",
            "content": "我既想被理解，又害怕被完全看见。",
            "privacy": "private",
            "preserve_verbatim": True,
            "recorded_at": "2026-09-04T11:30:00+08:00",
            "effective_at": "2024-05-01T00:00:00+08:00",
            "context": "回看两年前的想法",
        },
    )

    assert response.status_code == 201
    material = response.json()
    assert material["id"] == "M001"
    assert material["content"] == "我既想被理解，又害怕被完全看见。"
    assert material["preserve_verbatim"] is True
    assert material["recorded_at"] == "2026-09-04T11:30:00+08:00"
    assert material["effective_at"] == "2024-05-01T00:00:00+08:00"


def test_material_rejects_time_without_timezone(client):
    response = client.post(
        "/api/v1/materials",
        json={
            "content": "没有时区的时间不应被接受",
            "recorded_at": "2026-09-04T11:30:00",
        },
    )

    assert response.status_code == 422
