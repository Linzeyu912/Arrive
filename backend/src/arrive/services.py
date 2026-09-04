from __future__ import annotations

import logging
import re
from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from . import models
from .config import get_settings
from .domain import Adoption, Agreement, Resonance
from .errors import ConflictError, InvariantError, NotFoundError
from .schemas import (
    MaterialCreate,
    PersonalPropositionCreate,
    ResponseEventCreate,
    SourceCreate,
    ThoughtMapCreate,
)
from .time_utils import dual_time, epoch_ms, exact_iso, now_in_default_timezone, require_aware

logger = logging.getLogger("arrive.services")

_DAILY_ORDINAL_ATTEMPTS = 3
_SOURCE_PROPOSITION_ID = re.compile(r"^SRC-\d{4,}/P\d{2,}$")
_PERSONAL_PROPOSITION_ID = re.compile(r"^P\d{3,}$")


def _pending_id() -> str:
    # Placeholder only survives until the autoincrement id is flushed; it must
    # stay within the String(32) column on databases that enforce lengths.
    return f"pending-{uuid4().hex[:12]}"


def _assign_public_id(
    session: Session,
    entity: models.Base,
    formatter: Callable[[int], str],
) -> None:
    session.add(entity)
    session.flush()
    entity.public_id = formatter(entity.id)


def _source_read_query():
    return select(models.Source).options(selectinload(models.Source.propositions))


def create_material(session: Session, payload: MaterialCreate) -> models.Material:
    effective = payload.effective_at or payload.recorded_at
    recorded_iso, recorded_epoch = dual_time(payload.recorded_at)
    effective_iso, effective_epoch = dual_time(effective)
    material = models.Material(
        public_id=_pending_id(),
        kind=payload.kind,
        content=payload.content,
        privacy=payload.privacy,
        preserve_verbatim=payload.preserve_verbatim,
        recorded_at=recorded_iso,
        recorded_at_epoch_ms=recorded_epoch,
        effective_at=effective_iso,
        effective_at_epoch_ms=effective_epoch,
        context=payload.context,
    )
    _assign_public_id(session, material, lambda material_id: f"M{material_id:03d}")
    session.commit()
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
    _assign_public_id(session, source, lambda source_id: f"SRC-{source_id:04d}")

    for ordinal, proposition_payload in enumerate(payload.propositions, start=1):
        session.add(
            models.SourceProposition(
                public_id=f"{source.public_id}/P{ordinal:02d}",
                source_id=source.id,
                ordinal=ordinal,
                text=proposition_payload.text,
                attribution=proposition_payload.attribution,
                created_at=exact_iso(created),
            )
        )

    session.commit()
    return source


def get_source(session: Session, source_id: str) -> models.Source:
    source = session.scalar(
        _source_read_query().where(models.Source.public_id == source_id)
    )
    if source is None:
        raise NotFoundError(f"source {source_id} was not found")
    return source


def list_sources(session: Session) -> list[models.Source]:
    return list(session.scalars(_source_read_query().order_by(models.Source.id)).unique())


def _create_personal_proposition_record(
    session: Session, payload: PersonalPropositionCreate
) -> models.PersonalProposition:
    if payload.origin_source_proposition_id:
        _require_source_proposition(session, payload.origin_source_proposition_id)

    proposition = models.PersonalProposition(
        public_id=_pending_id(),
        text=payload.text,
        origin_source_proposition_id=payload.origin_source_proposition_id,
        created_at=exact_iso(now_in_default_timezone()),
        privacy=payload.privacy,
    )
    _assign_public_id(session, proposition, lambda proposition_id: f"P{proposition_id:03d}")
    return proposition


def create_personal_proposition(
    session: Session,
    payload: PersonalPropositionCreate,
) -> models.PersonalProposition:
    proposition = _create_personal_proposition_record(session, payload)
    session.commit()
    return proposition


def list_personal_propositions(
    session: Session,
) -> list[models.PersonalProposition]:
    return list(
        session.scalars(
            select(models.PersonalProposition).order_by(models.PersonalProposition.id)
        )
    )


def _require_source_proposition(session: Session, proposition_id: str) -> None:
    found = session.scalar(
        select(1).where(models.SourceProposition.public_id == proposition_id)
    )
    if found is None:
        raise NotFoundError(f"source proposition {proposition_id} was not found")


def _require_personal_proposition(session: Session, proposition_id: str) -> None:
    found = session.scalar(
        select(1).where(models.PersonalProposition.public_id == proposition_id)
    )
    if found is None:
        raise NotFoundError(f"personal proposition {proposition_id} was not found")


def _resolve_target(session: Session, target_id: str) -> str:
    if _SOURCE_PROPOSITION_ID.match(target_id):
        _require_source_proposition(session, target_id)
        return "source_proposition"
    if _PERSONAL_PROPOSITION_ID.match(target_id):
        _require_personal_proposition(session, target_id)
        return "personal_proposition"
    raise InvariantError(
        "target_id must be a source proposition such as SRC-0001/P04 "
        "or a personal proposition such as P001"
    )


def _next_daily_ordinal(session: Session, recorded_date: str) -> int:
    max_ordinal = session.scalar(
        select(func.max(models.ResponseEvent.daily_ordinal)).where(
            models.ResponseEvent.recorded_date == recorded_date
        )
    )
    return (max_ordinal or 0) + 1


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
    recorded_iso, recorded_epoch = dual_time(recorded)
    effective_iso, effective_epoch = dual_time(effective)
    recorded_date = recorded.astimezone(get_settings().timezone).date().isoformat()

    for attempt in range(1, _DAILY_ORDINAL_ATTEMPTS + 1):
        daily_ordinal = _next_daily_ordinal(session, recorded_date)
        public_id = f"RSP-{recorded_date.replace('-', '')}-{daily_ordinal:03d}"

        personal_proposition_id = None
        if payload.creates_personal_proposition_text:
            personal = _create_personal_proposition_record(
                session,
                PersonalPropositionCreate(
                    text=payload.creates_personal_proposition_text,
                    origin_source_proposition_id=(
                        payload.target_id if target_type == "source_proposition" else None
                    ),
                    privacy=payload.personal_proposition_privacy,
                ),
            )
            personal_proposition_id = personal.public_id

        event = models.ResponseEvent(
            public_id=public_id,
            target_id=payload.target_id,
            target_type=target_type,
            recorded_at=recorded_iso,
            recorded_at_epoch_ms=recorded_epoch,
            recorded_date=recorded_date,
            daily_ordinal=daily_ordinal,
            effective_at=effective_iso,
            effective_at_epoch_ms=effective_epoch,
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
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            logger.warning(
                "daily ordinal conflict on %s, retrying (attempt %d of %d)",
                public_id,
                attempt,
                _DAILY_ORDINAL_ATTEMPTS,
            )
            continue
        return event

    raise ConflictError(
        "could not allocate a unique daily ordinal for the response event; "
        "please retry the request"
    )


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


_AXIS_DEFAULTS = {
    "resonance": Resonance.UNSPECIFIED,
    "agreement": Agreement.UNSPECIFIED,
    "adoption": Adoption.UNDECIDED,
}


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
        name: {"value": default.value, "event_id": None, "effective_at": None}
        for name, default in _AXIS_DEFAULTS.items()
    }

    for event in events:
        for axis_name, default in _AXIS_DEFAULTS.items():
            value = getattr(event, axis_name)
            if value != default:
                axes[axis_name] = {
                    "value": value.value,
                    "event_id": event.public_id,
                    "effective_at": event.effective_at,
                }

    return {
        "target_id": target_id,
        "as_of": exact_iso(as_of),
        **axes,
        "event_count": len(events),
    }


def _require_materials(session: Session, material_ids: list[str]) -> None:
    if not material_ids:
        return
    found = set(
        session.scalars(
            select(models.Material.public_id).where(
                models.Material.public_id.in_(material_ids)
            )
        )
    )
    missing = sorted(set(material_ids) - found)
    if missing:
        raise InvariantError(
            "source_material_ids must reference existing materials: "
            + ", ".join(missing)
        )


def create_thought_map(session: Session, payload: ThoughtMapCreate) -> models.ThoughtMap:
    _require_materials(session, payload.source_material_ids)
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
    _assign_public_id(session, thought_map, lambda map_id: f"MAP-{map_id:04d}")
    session.commit()
    return thought_map


def get_thought_map(session: Session, map_id: str) -> models.ThoughtMap:
    thought_map = session.scalar(
        select(models.ThoughtMap).where(models.ThoughtMap.public_id == map_id)
    )
    if thought_map is None:
        raise NotFoundError(f"thought map {map_id} was not found")
    return thought_map
