from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
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
from .serializers import (
    material_read,
    personal_proposition_read,
    response_event_read,
    source_read,
    thought_map_read,
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


@router.post(
    "/materials", response_model=MaterialRead, status_code=status.HTTP_201_CREATED
)
def post_material(
    payload: MaterialCreate, session: Session = Depends(get_session)
) -> MaterialRead:
    return material_read(create_material(session, payload))


@router.get("/materials", response_model=list[MaterialRead])
def get_materials(session: Session = Depends(get_session)) -> list[MaterialRead]:
    return [material_read(item) for item in list_materials(session)]


@router.post(
    "/sources", response_model=SourceRead, status_code=status.HTTP_201_CREATED
)
def post_source(
    payload: SourceCreate, session: Session = Depends(get_session)
) -> SourceRead:
    return source_read(create_source(session, payload))


@router.get("/sources", response_model=list[SourceRead])
def get_sources(session: Session = Depends(get_session)) -> list[SourceRead]:
    return [source_read(item) for item in list_sources(session)]


@router.get("/sources/{source_id}", response_model=SourceRead)
def get_source_by_id(
    source_id: str, session: Session = Depends(get_session)
) -> SourceRead:
    return source_read(get_source(session, source_id))


@router.post(
    "/personal-propositions",
    response_model=PersonalPropositionRead,
    status_code=status.HTTP_201_CREATED,
)
def post_personal_proposition(
    payload: PersonalPropositionCreate, session: Session = Depends(get_session)
) -> PersonalPropositionRead:
    return personal_proposition_read(create_personal_proposition(session, payload))


@router.get(
    "/personal-propositions", response_model=list[PersonalPropositionRead]
)
def get_personal_propositions(
    session: Session = Depends(get_session),
) -> list[PersonalPropositionRead]:
    return [
        personal_proposition_read(item)
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
    return response_event_read(create_response_event(session, payload))


@router.get(
    "/responses/timeline/{target_id:path}", response_model=list[ResponseEventRead]
)
def get_response_timeline(
    target_id: str, session: Session = Depends(get_session)
) -> list[ResponseEventRead]:
    return [
        response_event_read(event) for event in response_timeline(session, target_id)
    ]


@router.get(
    "/responses/snapshot/{target_id:path}", response_model=StanceSnapshot
)
def get_stance_snapshot(
    target_id: str,
    as_of: datetime | None = Query(default=None),
    session: Session = Depends(get_session),
) -> StanceSnapshot:
    snapshot_time = as_of or now_in_default_timezone()
    require_aware(snapshot_time, "as_of")
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
    return thought_map_read(create_thought_map(session, payload))


@router.get("/thought-maps/{map_id}", response_model=ThoughtMapRead)
def get_thought_map_by_id(
    map_id: str, session: Session = Depends(get_session)
) -> ThoughtMapRead:
    return thought_map_read(get_thought_map(session, map_id))
