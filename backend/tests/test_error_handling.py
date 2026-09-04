from sqlalchemy.exc import IntegrityError


def test_unexpected_integrity_error_maps_to_stable_conflict(client, monkeypatch):
    def raise_integrity_error(session, payload):
        raise IntegrityError("INSERT", {}, Exception("UNIQUE constraint failed"))

    monkeypatch.setattr("arrive.api.create_material", raise_integrity_error)

    response = client.post("/api/v1/materials", json={"content": "合成内容"})

    assert response.status_code == 409
    assert response.json()["detail"] == "the request conflicts with stored records"
