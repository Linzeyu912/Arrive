from .conftest import create_source


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
        "original_words": "这个合成示例有启发，但结论仍待确认。",
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
        original_words="现在接受这个合成判断，但保留最初的犹豫记录。",
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
            "表达既需要结构，也需要保留尚未解决的复杂性。"
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


def test_snapshot_rejects_as_of_without_timezone(client):
    assert create_source(client).status_code == 201

    response = client.get(
        "/api/v1/responses/snapshot/SRC-0001/P01",
        params={"as_of": "2026-01-15T00:00:00"},
    )

    assert response.status_code == 422


def test_daily_ordinal_increments_within_day_and_resets_next_day(client):
    assert create_source(client).status_code == 201

    first = post_response(client)
    second = post_response(client, original_words="同一天的第二条合成回应。")
    assert [first.json()["id"], second.json()["id"]] == [
        "RSP-20260101-001",
        "RSP-20260101-002",
    ]

    next_day = post_response(
        client,
        recorded_at="2026-01-02T09:00:00+08:00",
        effective_at="2026-01-02T09:00:00+08:00",
        original_words="第二天的第一条合成回应。",
    )
    assert next_day.json()["id"] == "RSP-20260102-001"


def test_rsp_day_bucket_uses_default_timezone_not_client_offset(client):
    assert create_source(client).status_code == 201

    shanghai = post_response(
        client,
        recorded_at="2026-01-02T09:00:00+08:00",
        effective_at="2026-01-02T09:00:00+08:00",
    )
    # Same instant expressed from New York: under the old client-offset rule
    # this would land in the 2026-01-01 bucket instead of sharing the day.
    new_york = post_response(
        client,
        recorded_at="2026-01-01T20:00:00-05:00",
        effective_at="2026-01-01T20:00:00-05:00",
    )

    assert shanghai.json()["id"] == "RSP-20260102-001"
    assert new_york.json()["id"] == "RSP-20260102-002"


def test_daily_ordinal_conflict_is_retried(client, monkeypatch):
    from arrive import services

    assert create_source(client).status_code == 201
    assert post_response(client).json()["id"] == "RSP-20260101-001"

    real_next = services._next_daily_ordinal
    calls = {"count": 0}

    def conflicting_then_real(session, recorded_date):
        calls["count"] += 1
        if calls["count"] == 1:
            return 1
        return real_next(session, recorded_date)

    monkeypatch.setattr(services, "_next_daily_ordinal", conflicting_then_real)

    response = post_response(client, original_words="编号冲突后重试成功的合成回应。")
    assert response.status_code == 201
    assert response.json()["id"] == "RSP-20260101-002"


def test_snapshot_tracks_adoption_axis_independently(client):
    assert create_source(client).status_code == 201
    first = post_response(client, adoption="undecided")
    assert first.status_code == 201

    january = client.get(
        "/api/v1/responses/snapshot/SRC-0001/P01",
        params={"as_of": "2026-01-15T00:00:00+08:00"},
    )
    assert january.json()["adoption"] == {
        "value": "undecided",
        "event_id": None,
        "effective_at": None,
    }

    second = post_response(
        client,
        recorded_at="2026-02-01T09:00:00+08:00",
        effective_at="2026-02-01T09:00:00+08:00",
        resonance="unspecified",
        adoption="adapt",
        original_words="后来决定采用这个合成判断的一部分。",
    )
    assert second.status_code == 201

    march = client.get(
        "/api/v1/responses/snapshot/SRC-0001/P01",
        params={"as_of": "2026-03-01T00:00:00+08:00"},
    )
    assert march.json()["adoption"] == {
        "value": "adapt",
        "event_id": second.json()["id"],
        "effective_at": "2026-02-01T09:00:00+08:00",
    }
    assert march.json()["resonance"]["value"] == "high"


def test_personal_proposition_can_be_a_response_target(client):
    proposition = client.post(
        "/api/v1/personal-propositions",
        json={"text": "表达需要保留未解之处。", "privacy": "private"},
    )
    assert proposition.status_code == 201
    assert proposition.json()["id"] == "P001"

    response = post_response(client, target_id="P001")
    assert response.status_code == 201

    timeline = client.get("/api/v1/responses/timeline/P001")
    assert timeline.status_code == 200
    assert [event["id"] for event in timeline.json()] == [response.json()["id"]]


def test_response_rejects_malformed_target_id(client):
    response = post_response(client, target_id="PROPOSITION-X")
    assert response.status_code == 422


def test_response_rejects_unknown_personal_proposition_target(client):
    response = post_response(client, target_id="P999")
    assert response.status_code == 404
