from __future__ import annotations

from datetime import datetime
from pathlib import PurePosixPath
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

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
AwareDatetime = Annotated[datetime, AfterValidator(require_aware)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReadModel(StrictModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


class MaterialCreate(StrictModel):
    kind: MaterialKind = MaterialKind.THOUGHT
    content: NonEmptyText
    privacy: Privacy = Privacy.PRIVATE
    preserve_verbatim: bool = False
    recorded_at: AwareDatetime = Field(default_factory=now_in_default_timezone)
    effective_at: AwareDatetime | None = None
    context: str | None = None


class MaterialRead(ReadModel):
    id: str = Field(validation_alias="public_id")
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
    original_url: HttpUrl | None = None
    title: NonEmptyText
    platform: str | None = None
    canonical_url: HttpUrl | None = None
    creator: str | None = None
    publisher: str | None = None
    published_at: str | None = None
    language: str | None = None
    topics: list[str] = Field(default_factory=list)
    stance: SourceStance = SourceStance.PENDING
    stance_as_of: AwareDatetime | None = None
    content_status: ContentStatus = ContentStatus.REGISTERED
    rights: Rights = Rights.UNKNOWN
    raw_archive_path: str | None = None
    raw_archive_sha256: str | None = Field(default=None, pattern=r"^[A-Fa-f0-9]{64}$")
    raw_archive_bytes: int | None = Field(default=None, ge=0)
    propositions: list[SourcePropositionCreate] = Field(default_factory=list)

    @model_validator(mode='after')
    def require_source_input(self):
        if not self.original_url and not self.raw_archive_path:
            raise ValueError('A source URL or archived file is required')
        return self

    @field_validator("raw_archive_path")
    @classmethod
    def archive_path_must_be_a_data_root_key(
        cls, value: str | None
    ) -> str | None:
        if value is None:
            return None

        normalized = value.replace("\\", "/")
        path = PurePosixPath(normalized)
        if (
            path.is_absolute()
            or ".." in path.parts
            or not path.parts
            or path.parts[0] != "raw"
        ):
            raise ValueError(
                "raw_archive_path must be a relative key below ARRIVE_DATA_DIR/raw"
            )
        return path.as_posix()


class SourcePropositionRead(ReadModel):
    id: str = Field(validation_alias="public_id")
    ordinal: int
    text: str
    attribution: PropositionAttribution
    created_at: str


class SourceRead(ReadModel):
    id: str = Field(validation_alias="public_id")
    kind: SourceKind
    platform: str | None
    original_url: str | None
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


class PersonalPropositionRead(ReadModel):
    id: str = Field(validation_alias="public_id")
    text: str
    origin_source_proposition_id: str | None
    privacy: Privacy
    created_at: str


class ResponseEventCreate(StrictModel):
    target_id: NonEmptyText
    recorded_at: AwareDatetime = Field(default_factory=now_in_default_timezone)
    effective_at: AwareDatetime | None = None
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


class ResponseEventRead(ReadModel):
    id: str = Field(validation_alias="public_id")
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


class ThoughtMapRead(ReadModel):
    id: str = Field(validation_alias="public_id")
    title: str
    version: str
    privacy: Privacy
    source_material_ids: list[str]
    nodes: list[ThoughtNode]
    edges: list[ThoughtEdge]
    created_at: str
