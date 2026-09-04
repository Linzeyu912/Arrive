from . import models
from .schemas import (
    MaterialRead,
    PersonalPropositionRead,
    ResponseEventRead,
    SourcePropositionRead,
    SourceRead,
    ThoughtMapRead,
)


def material_read(material: models.Material) -> MaterialRead:
    return MaterialRead(
        id=material.public_id,
        kind=material.kind,
        content=material.content,
        privacy=material.privacy,
        preserve_verbatim=material.preserve_verbatim,
        recorded_at=material.recorded_at,
        effective_at=material.effective_at,
        context=material.context,
    )


def source_read(source: models.Source) -> SourceRead:
    return SourceRead(
        id=source.public_id,
        kind=source.kind,
        platform=source.platform,
        original_url=source.original_url,
        canonical_url=source.canonical_url,
        title=source.title,
        creator=source.creator,
        publisher=source.publisher,
        published_at=source.published_at,
        language=source.language,
        topics=source.topics,
        stance=source.stance,
        stance_as_of=source.stance_as_of,
        content_status=source.content_status,
        rights=source.rights,
        raw_archive_path=source.raw_archive_path,
        raw_archive_sha256=source.raw_archive_sha256,
        raw_archive_bytes=source.raw_archive_bytes,
        created_at=source.created_at,
        propositions=[
            SourcePropositionRead(
                id=proposition.public_id,
                ordinal=proposition.ordinal,
                text=proposition.text,
                attribution=proposition.attribution,
                created_at=proposition.created_at,
            )
            for proposition in source.propositions
        ],
    )


def personal_proposition_read(
    proposition: models.PersonalProposition,
) -> PersonalPropositionRead:
    return PersonalPropositionRead(
        id=proposition.public_id,
        text=proposition.text,
        origin_source_proposition_id=proposition.origin_source_proposition_id,
        privacy=proposition.privacy,
        created_at=proposition.created_at,
    )


def response_event_read(event: models.ResponseEvent) -> ResponseEventRead:
    return ResponseEventRead(
        id=event.public_id,
        target_id=event.target_id,
        target_type=event.target_type,
        recorded_at=event.recorded_at,
        effective_at=event.effective_at,
        time_precision=event.time_precision,
        resonance=event.resonance,
        agreement=event.agreement,
        adoption=event.adoption,
        confidence=event.confidence,
        original_words=event.original_words,
        context=event.context,
        assistant_summary=event.assistant_summary,
        supersedes=event.supersedes,
        creates_personal_proposition_id=event.creates_personal_proposition_id,
    )


def thought_map_read(thought_map: models.ThoughtMap) -> ThoughtMapRead:
    return ThoughtMapRead(
        id=thought_map.public_id,
        title=thought_map.title,
        version=thought_map.version,
        privacy=thought_map.privacy,
        source_material_ids=thought_map.source_material_ids,
        nodes=thought_map.nodes,
        edges=thought_map.edges,
        created_at=thought_map.created_at,
    )
