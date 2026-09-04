from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

from .domain import (
    Adoption,
    Agreement,
    Confidence,
    ContentStatus,
    MaterialKind,
    Privacy,
    PropositionAttribution,
    Resonance,
    Rights,
    SourceKind,
    SourceStance,
    ThoughtNodeType,
    ThoughtRelation,
    TimePrecision,
)
from .time_utils import now_in_default_timezone, require_aware


NonEmptyText = Annotated[str, Field(min_length=1)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MaterialCreate(StrictModel):
    kind: MaterialKind = MaterialKind.THOUGHT
    content: NonEmptyText
    privacy: Privacy = Privacy.PRIVATE
    preserve_verbatim: bool = False
    recorded_at: datetime = Field(default_factory=now_in_default_timezone)
    effective_at: datetime | None = None
    context: str | None = None

    @field_validator("recorded_at", "effective_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None:
            require_aware(value)
        return value


class MaterialRead(StrictModel):
    id: str
    kind: MaterialKind
    content: str
    privacy: Privacy
    preserve_verbatim: bool
    recorded_at: str
    effective_at: str
    context: str | None


class SourcePropositionCreate(StrictModel):
    text: NonEmptyText
    attribution: PropositionAttribution = PropositionAttribution.COLLABORATOR_SUMMARY


class SourceCreate(StrictModel):
    kind: SourceKind
    original_url: HttpUrl
    title: NonEmptyText
    platform: str | None = None
    canonical_url: HttpUrl | None = None
    creator: str | None = None
    publisher: str | None = None
    published_at: str | None = None
    language: str | None = None
    topics: list[str] = Field(default_factory=list)
    stance: SourceStance = SourceStance.PENDING
    stance_as_of: datetime | None = None
    content_status: ContentStatus = ContentStatus.REGISTERED
    rights: Rights = Rights.UNKNOWN
    raw_archive_path: str | None = None
    raw_archive_sha256: str | None = Field(default=None, pattern=r"^[A-Fa-f0-9]{64}$")
    raw_archive_bytes: int | None = Field(default=None, ge=0)
    propositions: list[SourcePropositionCreate] = Field(default_factory=list)

    @field_validator("stance_as_of")
    @classmethod
    def stance_time_must_be_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None:
            require_aware(value)
        return value


class SourcePropositionRead(StrictModel):
    id: str
    ordinal: int
    text: str
    attribution: PropositionAttribution
    created_at: str


class SourceRead(StrictModel):
    id: str
    kind: SourceKind
    platform: str | None
    original_url: str
    canonical_url: str | None
    title: str
    creator: str | None
    publisher: str | None
    published_at: str | None
    language: str | None
    topics: list[str]
    stance: SourceStance
    stance_as_of: str | None
    content_status: ContentStatus
    rights: Rights
    raw_archive_path: str | None
    raw_archive_sha256: str | None
    raw_archive_bytes: int | None
    created_at: str
    propositions: list[SourcePropositionRead]


class PersonalPropositionCreate(StrictModel):
    text: NonEmptyText
    origin_source_proposition_id: str | None = None
    privacy: Privacy = Privacy.PRIVATE


class PersonalPropositionRead(StrictModel):
    id: str
    text: str
    origin_source_proposition_id: str | None
    privacy: Privacy
    created_at: str


class ResponseEventCreate(StrictModel):
    target_id: NonEmptyText
    recorded_at: datetime = Field(default_factory=now_in_default_timezone)
    effective_at: datetime | None = None
    time_precision: TimePrecision = TimePrecision.MINUTE
    resonance: Resonance = Resonance.UNSPECIFIED
    agreement: Agreement = Agreement.UNSPECIFIED
    adoption: Adoption = Adoption.UNDECIDED
    confidence: Confidence = Confidence.MEDIUM
    original_words: str | None = None
    context: str | None = None
    assistant_summary: str | None = None
    supersedes: str | None = None
    creates_personal_proposition_text: str | None = None
    personal_proposition_privacy: Privacy = Privacy.PRIVATE

    @field_validator("recorded_at", "effective_at")
    @classmethod
    def response_times_must_be_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None:
            require_aware(value)
        return value

    @model_validator(mode="after")
    def adoption_controls_personal_proposition(self) -> ResponseEventCreate:
        if self.creates_personal_proposition_text and self.adoption not in {
            Adoption.ADOPT,
            Adoption.ADAPT,
        }:
            raise ValueError(
                "creates_personal_proposition_text requires adoption=adopt or adapt"
            )
        return self


class ResponseEventRead(StrictModel):
    id: str
    target_id: str
    target_type: Literal["source_proposition", "personal_proposition"]
    recorded_at: str
    effective_at: str
    time_precision: TimePrecision
    resonance: Resonance
    agreement: Agreement
    adoption: Adoption
    confidence: Confidence
    original_words: str | None
    context: str | None
    assistant_summary: str | None
    supersedes: str | None
    creates_personal_proposition_id: str | None


class AxisSnapshot(StrictModel):
    value: str
    event_id: str | None
    effective_at: str | None


class StanceSnapshot(StrictModel):
    target_id: str
    as_of: str
    resonance: AxisSnapshot
    agreement: AxisSnapshot
    adoption: AxisSnapshot
    event_count: int


class ThoughtNode(StrictModel):
    id: NonEmptyText
    type: ThoughtNodeType
    text: NonEmptyText
    status: str = "pending"


class ThoughtEdge(StrictModel):
    source: NonEmptyText
    target: NonEmptyText
    relation: ThoughtRelation


class ThoughtMapCreate(StrictModel):
    title: NonEmptyText
    version: str = "v0.1"
    privacy: Privacy = Privacy.PRIVATE
    source_material_ids: list[str] = Field(default_factory=list)
    nodes: list[ThoughtNode] = Field(default_factory=list)
    edges: list[ThoughtEdge] = Field(default_factory=list)

    @model_validator(mode="after")
    def edges_reference_existing_nodes(self) -> ThoughtMapCreate:
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("thought-map node ids must be unique")
        known = set(node_ids)
        for edge in self.edges:
            if edge.source not in known or edge.target not in known:
                raise ValueError("thought-map edges must reference existing node ids")
            if edge.source == edge.target:
                raise ValueError("thought-map edges cannot point to the same node")
        return self


class ThoughtMapRead(StrictModel):
    id: str
    title: str
    version: str
    privacy: Privacy
    source_material_ids: list[str]
    nodes: list[ThoughtNode]
    edges: list[ThoughtEdge]
    created_at: str
