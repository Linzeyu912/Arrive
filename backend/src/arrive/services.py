from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from . import models
from .domain import Adoption, Agreement, Resonance
from .errors import ConflictError, InvariantError, NotFoundError
from .schemas import (
    MaterialCreate,
    PersonalPropositionCreate,
    ResponseEventCreate,
    SourceCreate,
    ThoughtMapCreate,
)
from .time_utils import epoch_ms, exact_iso, now_in_default_timezone, require_aware


def _pending_id() -> str:
    return f"pending-{uuid4().hex}"


def _source_read_query():
    return select(models.Source).options(selectinload(models.Source.propositions))


def create_material(session: Session, payload: MaterialCreate) -> models.Material:
    effective = payload.effective_at or payload.recorded_at
    material = models.Material(
        public_id=_pending_id(),
        kind=payload.kind,
        content=payload.content,
        privacy=payload.privacy,
        preserve_verbatim=payload.preserve_verbatim,
        recorded_at=exact_iso(payload.recorded_at),
        recorded_at_epoch_ms=epoch_ms(payload.recorded_at),
        effective_at=exact_iso(effective),
        effective_at_epoch_ms=epoch_ms(effective),
        context=payload.context,
    )
    session.add(material)
    session.flush()
    material.public_id = f"M{material.id:03d}"
    session.commit()
    session.refresh(material)
    return material


def list_materials(session: Session) -> list[models.Material]:
    return list(session.scalars(select(models.Material).order_by(models.Material.id)))


def create_source(session: Session, payload: SourceCreate) -> models.Source:
    created = now_in_default_timezone()
    source = models.Source(
        public_id=_pending_id(),
        kind=payload.kind,
        platform=payload.platform,
        original_url=str(payload.original_url),
        canonical_url=str(payload.canonical_url) if payload.canonical_url else None,
        title=payload.title,
        creator=payload.creator,
        publisher=payload.publisher,
        published_at=payload.published_at,
        language=payload.language,
        topics=payload.topics,
        stance=payload.stance,
        stance_as_of=exact_iso(payload.stance_as_of) if payload.stance_as_of else None,
        content_status=payload.content_status,
        rights=payload.rights,
        raw_archive_path=payload.raw_archive_path,
        raw_archive_sha256=(
            payload.raw_archive_sha256.upper() if payload.raw_archive_sha256 else None
        ),
        raw_archive_bytes=payload.raw_archive_bytes,
        created_at=exact_iso(created),
    )
    session.add(source)
    session.flush()
    source.public_id = f"SRC-{source.id:04d}"

    for ordinal, proposition_payload in enumerate(payload.propositions, start=1):
        proposition = models.SourceProposition(
            public_id=f"{source.public_id}/P{ordinal:02d}",
            source_id=source.id,
            ordinal=ordinal,
            text=proposition_payload.text,
            attribution=proposition_payload.attribution,
            created_at=exact_iso(created),
        )
        session.add(proposition)

    session.commit()
    return get_source(session, source.public_id)


def get_source(session: Session, source_id: str) -> models.Source:
    source = session.scalar(
        _source_read_query().where(models.Source.public_id == source_id)
    )
    if source is None:
        raise NotFoundError(f"source {source_id} was not found")
    return source


def list_sources(session: Session) -> list[models.Source]:
    return list(session.scalars(_source_read_query().order_by(models.Source.id)).unique())


def create_personal_proposition(
    session: Session,
    payload: PersonalPropositionCreate,
    *,
    commit: bool = True,
) -> models.PersonalProposition:
    if payload.origin_source_proposition_id:
        _get_source_proposition(session, payload.origin_source_proposition_id)

    proposition = models.PersonalProposition(
        public_id=_pending_id(),
        text=payload.text,
        origin_source_proposition_id=payload.origin_source_proposition_id,
        created_at=exact_iso(now_in_default_timezone()),
        privacy=payload.privacy,
    )
    session.add(proposition)
    session.flush()
    proposition.public_id = f"P{proposition.id:03d}"
    if commit:
        session.commit()
        session.refresh(proposition)
    return proposition


def list_personal_propositions(
    session: Session,
) -> list[models.PersonalProposition]:
    return list(
        session.scalars(
            select(models.PersonalProposition).order_by(models.PersonalProposition.id)
        )
    )


def _get_source_proposition(
    session: Session, proposition_id: str
) -> models.SourceProposition:
    proposition = session.scalar(
        select(models.SourceProposition).where(
            models.SourceProposition.public_id == proposition_id
        )
    )
    if proposition is None:
        raise NotFoundError(f"source proposition {proposition_id} was not found")
    return proposition


def _resolve_target(session: Session, target_id: str) -> str:
    if target_id.startswith("SRC-"):
        _get_source_proposition(session, target_id)
        return "source_proposition"
    if target_id.startswith("P"):
        proposition = session.scalar(
            select(models.PersonalProposition).where(
                models.PersonalProposition.public_id == target_id
            )
        )
        if proposition is None:
            raise NotFoundError(f"personal proposition {target_id} was not found")
        return "personal_proposition"
    raise InvariantError(
        "target_id must be a source proposition such as SRC-0001/P04 "
        "or a personal proposition such as P001"
    )


def create_response_event(
    session: Session, payload: ResponseEventCreate
) -> models.ResponseEvent:
    target_type = _resolve_target(session, payload.target_id)

    if payload.supersedes:
        previous = session.scalar(
            select(models.ResponseEvent).where(
                models.ResponseEvent.public_id == payload.supersedes
            )
        )
        if previous is None:
            raise NotFoundError(f"response event {payload.supersedes} was not found")
        if previous.target_id != payload.target_id:
            raise ConflictError("supersedes must reference an event for the same target")

    recorded = payload.recorded_at
    effective = payload.effective_at or recorded
    recorded_date = recorded.date().isoformat()
    max_ordinal = session.scalar(
        select(func.max(models.ResponseEvent.daily_ordinal)).where(
            models.ResponseEvent.recorded_date == recorded_date
        )
    )
    daily_ordinal = (max_ordinal or 0) + 1
    public_id = f"RSP-{recorded_date.replace('-', '')}-{daily_ordinal:03d}"

    personal_proposition_id = None
    if payload.creates_personal_proposition_text:
        personal = create_personal_proposition(
            session,
            PersonalPropositionCreate(
                text=payload.creates_personal_proposition_text,
                origin_source_proposition_id=(
                    payload.target_id if target_type == "source_proposition" else None
                ),
                privacy=payload.personal_proposition_privacy,
            ),
            commit=False,
        )
        personal_proposition_id = personal.public_id

    event = models.ResponseEvent(
        public_id=public_id,
        target_id=payload.target_id,
        target_type=target_type,
        recorded_at=exact_iso(recorded),
        recorded_at_epoch_ms=epoch_ms(recorded),
        recorded_date=recorded_date,
        daily_ordinal=daily_ordinal,
        effective_at=exact_iso(effective),
        effective_at_epoch_ms=epoch_ms(effective),
        time_precision=payload.time_precision,
        resonance=payload.resonance,
        agreement=payload.agreement,
        adoption=payload.adoption,
        confidence=payload.confidence,
        original_words=payload.original_words,
        context=payload.context,
        assistant_summary=payload.assistant_summary,
        supersedes=payload.supersedes,
        creates_personal_proposition_id=personal_proposition_id,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def response_timeline(session: Session, target_id: str) -> list[models.ResponseEvent]:
    _resolve_target(session, target_id)
    statement = (
        select(models.ResponseEvent)
        .where(models.ResponseEvent.target_id == target_id)
        .order_by(
            models.ResponseEvent.effective_at_epoch_ms,
            models.ResponseEvent.recorded_at_epoch_ms,
            models.ResponseEvent.id,
        )
    )
    return list(session.scalars(statement))


def stance_snapshot(
    session: Session, target_id: str, as_of: datetime
) -> dict[str, object]:
    require_aware(as_of, "as_of")
    _resolve_target(session, target_id)
    events = list(
        session.scalars(
            select(models.ResponseEvent)
            .where(
                models.ResponseEvent.target_id == target_id,
                models.ResponseEvent.effective_at_epoch_ms <= epoch_ms(as_of),
            )
            .order_by(
                models.ResponseEvent.effective_at_epoch_ms,
                models.ResponseEvent.recorded_at_epoch_ms,
                models.ResponseEvent.id,
            )
        )
    )

    axes: dict[str, dict[str, str | None]] = {
        "resonance": {"value": Resonance.UNSPECIFIED.value, "event_id": None, "effective_at": None},
        "agreement": {"value": Agreement.UNSPECIFIED.value, "event_id": None, "effective_at": None},
        "adoption": {"value": Adoption.UNDECIDED.value, "event_id": None, "effective_at": None},
    }

    for event in events:
        if event.resonance != Resonance.UNSPECIFIED:
            axes["resonance"] = {
                "value": event.resonance.value,
                "event_id": event.public_id,
                "effective_at": event.effective_at,
            }
        if event.agreement != Agreement.UNSPECIFIED:
            axes["agreement"] = {
                "value": event.agreement.value,
                "event_id": event.public_id,
                "effective_at": event.effective_at,
            }
        if event.adoption != Adoption.UNDECIDED:
            axes["adoption"] = {
                "value": event.adoption.value,
                "event_id": event.public_id,
                "effective_at": event.effective_at,
            }

    return {
        "target_id": target_id,
        "as_of": exact_iso(as_of),
        **axes,
        "event_count": len(events),
    }


def create_thought_map(session: Session, payload: ThoughtMapCreate) -> models.ThoughtMap:
    thought_map = models.ThoughtMap(
        public_id=_pending_id(),
        title=payload.title,
        version=payload.version,
        privacy=payload.privacy,
        source_material_ids=payload.source_material_ids,
        nodes=[node.model_dump(mode="json") for node in payload.nodes],
        edges=[edge.model_dump(mode="json") for edge in payload.edges],
        created_at=exact_iso(now_in_default_timezone()),
    )
    session.add(thought_map)
    session.flush()
    thought_map.public_id = f"MAP-{thought_map.id:04d}"
    session.commit()
    session.refresh(thought_map)
    return thought_map


def get_thought_map(session: Session, map_id: str) -> models.ThoughtMap:
    thought_map = session.scalar(
        select(models.ThoughtMap).where(models.ThoughtMap.public_id == map_id)
    )
    if thought_map is None:
        raise NotFoundError(f"thought map {map_id} was not found")
    return thought_map
