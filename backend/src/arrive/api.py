from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from pydantic import AfterValidator
from sqlalchemy.orm import Session

from .database import get_session
from .schemas import (
    MaterialCreate,
    MaterialRead,
    PersonalPropositionCreate,
    PersonalPropositionRead,
    ResponseEventCreate,
    ResponseEventRead,
    SourceCreate,
    SourceRead,
    StanceSnapshot,
    ThoughtMapCreate,
    ThoughtMapRead,
)
from .services import (
    create_material,
    create_personal_proposition,
    create_response_event,
    create_source,
    create_thought_map,
    get_source,
    get_thought_map,
    list_materials,
    list_personal_propositions,
    list_sources,
    response_timeline,
    stance_snapshot,
)
from .time_utils import now_in_default_timezone, require_aware


router = APIRouter()


@router.get("/local-records")
def local_records(session: Session = Depends(get_session)):
    from sqlalchemy import select
    from .models import LegacyDocument
    return [dict(id=row.id, relative_key=row.relative_key, category=row.category,
                 source_id=row.source_id, status=row.status, note=row.note,
                 recorded_at=row.recorded_at)
            for row in session.scalars(select(LegacyDocument).order_by(LegacyDocument.id.desc()))]


@router.get("/local-records/{record_id}")
def local_record(record_id: int, session: Session = Depends(get_session)):
    from .models import LegacyDocument
    from .errors import NotFoundError
    row = session.get(LegacyDocument, record_id)
    if row is None:
        raise NotFoundError("local record not found")
    return dict(id=row.id, content=row.content, sha256=row.sha256)


@router.post(
    "/materials", response_model=MaterialRead, status_code=status.HTTP_201_CREATED
)
def post_material(
    payload: MaterialCreate, session: Session = Depends(get_session)
) -> MaterialRead:
    return MaterialRead.model_validate(create_material(session, payload))


@router.get("/materials", response_model=list[MaterialRead])
def get_materials(session: Session = Depends(get_session)) -> list[MaterialRead]:
    return [MaterialRead.model_validate(item) for item in list_materials(session)]


@router.post(
    "/sources", response_model=SourceRead, status_code=status.HTTP_201_CREATED
)
def post_source(
    payload: SourceCreate, session: Session = Depends(get_session)
) -> SourceRead:
    return SourceRead.model_validate(create_source(session, payload))


@router.get("/sources", response_model=list[SourceRead])
def get_sources(session: Session = Depends(get_session)) -> list[SourceRead]:
    return [SourceRead.model_validate(item) for item in list_sources(session)]


@router.get("/sources/{source_id}", response_model=SourceRead)
def get_source_by_id(
    source_id: str, session: Session = Depends(get_session)
) -> SourceRead:
    return SourceRead.model_validate(get_source(session, source_id))


@router.post(
    "/personal-propositions",
    response_model=PersonalPropositionRead,
    status_code=status.HTTP_201_CREATED,
)
def post_personal_proposition(
    payload: PersonalPropositionCreate, session: Session = Depends(get_session)
) -> PersonalPropositionRead:
    return PersonalPropositionRead.model_validate(
        create_personal_proposition(session, payload)
    )


@router.get(
    "/personal-propositions", response_model=list[PersonalPropositionRead]
)
def get_personal_propositions(
    session: Session = Depends(get_session),
) -> list[PersonalPropositionRead]:
    return [
        PersonalPropositionRead.model_validate(item)
        for item in list_personal_propositions(session)
    ]


@router.post(
    "/responses",
    response_model=ResponseEventRead,
    status_code=status.HTTP_201_CREATED,
)
def post_response(
    payload: ResponseEventCreate, session: Session = Depends(get_session)
) -> ResponseEventRead:
    return ResponseEventRead.model_validate(create_response_event(session, payload))


@router.get(
    "/responses/timeline/{target_id:path}", response_model=list[ResponseEventRead]
)
def get_response_timeline(
    target_id: str, session: Session = Depends(get_session)
) -> list[ResponseEventRead]:
    return [
        ResponseEventRead.model_validate(event)
        for event in response_timeline(session, target_id)
    ]


@router.get(
    "/responses/snapshot/{target_id:path}", response_model=StanceSnapshot
)
def get_stance_snapshot(
    target_id: str,
    as_of: Annotated[
        datetime | None, AfterValidator(require_aware), Query()
    ] = None,
    session: Session = Depends(get_session),
) -> StanceSnapshot:
    snapshot_time = as_of or now_in_default_timezone()
    return StanceSnapshot.model_validate(
        stance_snapshot(session, target_id, snapshot_time)
    )


@router.post(
    "/thought-maps",
    response_model=ThoughtMapRead,
    status_code=status.HTTP_201_CREATED,
)
def post_thought_map(
    payload: ThoughtMapCreate, session: Session = Depends(get_session)
) -> ThoughtMapRead:
    return ThoughtMapRead.model_validate(create_thought_map(session, payload))


@router.get("/thought-maps/{map_id}", response_model=ThoughtMapRead)
def get_thought_map_by_id(
    map_id: str, session: Session = Depends(get_session)
) -> ThoughtMapRead:
    return ThoughtMapRead.model_validate(get_thought_map(session, map_id))
