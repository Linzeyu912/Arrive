def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "arrive-backend",
        "version": "0.1.0",
    }
