from .test_sources import create_source


def post_response(client, **overrides):
    payload = {
        "target_id": "SRC-0001/P01",
        "recorded_at": "2026-01-01T09:00:00+08:00",
        "effective_at": "2026-01-01T09:00:00+08:00",
        "time_precision": "minute",
        "resonance": "high",
        "agreement": "uncertain",
        "adoption": "undecided",
        "confidence": "medium",
        "original_words": "这句话很打动我，但我还没有完全想清楚。",
    }
    payload.update(overrides)
    return client.post("/api/v1/responses", json=payload)


def test_response_history_is_append_only_and_snapshot_is_axis_aware(client):
    assert create_source(client).status_code == 201

    first = post_response(client)
    assert first.status_code == 201
    assert first.json()["id"] == "RSP-20260101-001"

    second = post_response(
        client,
        recorded_at="2026-02-01T09:00:00+08:00",
        effective_at="2026-02-01T09:00:00+08:00",
        resonance="unspecified",
        agreement="agree",
        supersedes=first.json()["id"],
        original_words="现在我认同它，但最初的犹豫仍然真实。",
    )
    assert second.status_code == 201

    january = client.get(
        "/api/v1/responses/snapshot/SRC-0001/P01",
        params={"as_of": "2026-01-15T00:00:00+08:00"},
    )
    assert january.status_code == 200
    assert january.json()["resonance"]["value"] == "high"
    assert january.json()["agreement"]["value"] == "uncertain"
    assert january.json()["event_count"] == 1

    february = client.get(
        "/api/v1/responses/snapshot/SRC-0001/P01",
        params={"as_of": "2026-02-15T00:00:00+08:00"},
    )
    assert february.status_code == 200
    assert february.json()["resonance"] == {
        "value": "high",
        "event_id": first.json()["id"],
        "effective_at": "2026-01-01T09:00:00+08:00",
    }
    assert february.json()["agreement"] == {
        "value": "agree",
        "event_id": second.json()["id"],
        "effective_at": "2026-02-01T09:00:00+08:00",
    }
    assert february.json()["event_count"] == 2

    timeline = client.get("/api/v1/responses/timeline/SRC-0001/P01")
    assert timeline.status_code == 200
    assert [event["id"] for event in timeline.json()] == [
        first.json()["id"],
        second.json()["id"],
    ]


def test_adoption_can_create_linked_personal_proposition(client):
    assert create_source(client).status_code == 201

    response = post_response(
        client,
        adoption="adapt",
        agreement="mostly_agree",
        creates_personal_proposition_text=(
            "爱包含可以练习的能力，也包含无法完全控制的感情。"
        ),
    )

    assert response.status_code == 201
    assert response.json()["creates_personal_proposition_id"] == "P001"

    propositions = client.get("/api/v1/personal-propositions")
    assert propositions.status_code == 200
    assert propositions.json()[0]["origin_source_proposition_id"] == "SRC-0001/P01"


def test_supersedes_must_reference_same_target(client):
    assert create_source(client).status_code == 201
    first = post_response(client)

    response = post_response(
        client,
        target_id="SRC-0001/P02",
        recorded_at="2026-01-02T09:00:00+08:00",
        effective_at="2026-01-02T09:00:00+08:00",
        supersedes=first.json()["id"],
    )

    assert response.status_code == 409
