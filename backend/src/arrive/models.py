from __future__ import annotations

from typing import Any

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
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
    TimePrecision,
)


def enum_type(enum_class):
    return SqlEnum(
        enum_class,
        values_callable=lambda members: [member.value for member in members],
        native_enum=False,
        validate_strings=True,
    )


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    kind: Mapped[MaterialKind] = mapped_column(enum_type(MaterialKind))
    content: Mapped[str] = mapped_column(Text)
    privacy: Mapped[Privacy] = mapped_column(enum_type(Privacy))
    preserve_verbatim: Mapped[bool] = mapped_column(Boolean, default=False)
    recorded_at: Mapped[str] = mapped_column(String(40))
    recorded_at_epoch_ms: Mapped[int] = mapped_column(BigInteger, index=True)
    effective_at: Mapped[str] = mapped_column(String(40))
    effective_at_epoch_ms: Mapped[int] = mapped_column(BigInteger, index=True)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    kind: Mapped[SourceKind] = mapped_column(enum_type(SourceKind))
    platform: Mapped[str | None] = mapped_column(String(200), nullable=True)
    original_url: Mapped[str] = mapped_column(Text)
    canonical_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    creator: Mapped[str | None] = mapped_column(String(300), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(300), nullable=True)
    published_at: Mapped[str | None] = mapped_column(String(80), nullable=True)
    language: Mapped[str | None] = mapped_column(String(40), nullable=True)
    topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    stance: Mapped[SourceStance] = mapped_column(enum_type(SourceStance))
    stance_as_of: Mapped[str | None] = mapped_column(String(40), nullable=True)
    content_status: Mapped[ContentStatus] = mapped_column(enum_type(ContentStatus))
    rights: Mapped[Rights] = mapped_column(enum_type(Rights))
    raw_archive_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_archive_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_archive_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[str] = mapped_column(String(40))

    propositions: Mapped[list[SourceProposition]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
        order_by="SourceProposition.ordinal",
    )


class SourceProposition(Base):
    __tablename__ = "source_propositions"
    __table_args__ = (UniqueConstraint("source_id", "ordinal"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), index=True)
    ordinal: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    attribution: Mapped[PropositionAttribution] = mapped_column(
        enum_type(PropositionAttribution)
    )
    created_at: Mapped[str] = mapped_column(String(40))

    source: Mapped[Source] = relationship(back_populates="propositions")


class PersonalProposition(Base):
    __tablename__ = "personal_propositions"

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    text: Mapped[str] = mapped_column(Text)
    origin_source_proposition_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    created_at: Mapped[str] = mapped_column(String(40))
    privacy: Mapped[Privacy] = mapped_column(enum_type(Privacy))


class ResponseEvent(Base):
    __tablename__ = "response_events"
    __table_args__ = (
        UniqueConstraint("recorded_date", "daily_ordinal"),
        CheckConstraint("daily_ordinal > 0", name="positive_daily_ordinal"),
        Index(
            "ix_response_events_target_effective",
            "target_id",
            "effective_at_epoch_ms",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    target_id: Mapped[str] = mapped_column(String(64))
    target_type: Mapped[str] = mapped_column(String(30))
    recorded_at: Mapped[str] = mapped_column(String(40))
    recorded_at_epoch_ms: Mapped[int] = mapped_column(BigInteger, index=True)
    recorded_date: Mapped[str] = mapped_column(String(10), index=True)
    daily_ordinal: Mapped[int] = mapped_column(Integer)
    effective_at: Mapped[str] = mapped_column(String(40))
    effective_at_epoch_ms: Mapped[int] = mapped_column(BigInteger, index=True)
    time_precision: Mapped[TimePrecision] = mapped_column(enum_type(TimePrecision))
    resonance: Mapped[Resonance] = mapped_column(enum_type(Resonance))
    agreement: Mapped[Agreement] = mapped_column(enum_type(Agreement))
    adoption: Mapped[Adoption] = mapped_column(enum_type(Adoption))
    confidence: Mapped[Confidence] = mapped_column(enum_type(Confidence))
    original_words: Mapped[str | None] = mapped_column(Text, nullable=True)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    assistant_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    supersedes: Mapped[str | None] = mapped_column(
        ForeignKey("response_events.public_id"), nullable=True
    )
    creates_personal_proposition_id: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )


class ThoughtMap(Base):
    __tablename__ = "thought_maps"

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    version: Mapped[str] = mapped_column(String(30))
    privacy: Mapped[Privacy] = mapped_column(enum_type(Privacy))
    source_material_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    nodes: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    edges: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    created_at: Mapped[str] = mapped_column(String(40))
