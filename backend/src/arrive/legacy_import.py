"""Conservative, repeatable adaptation of local legacy Markdown files.

Original files remain untouched. Only explicit source cards are projected into
domain tables; other records remain readable archives, never inferred beliefs.
"""
from datetime import datetime
import hashlib
from pathlib import Path
import re

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import yaml

from .config import data_path
from .models import LegacyDocument, Source, SourceProposition
from .schemas import SourceCreate
from .time_utils import now_in_default_timezone


class MetadataLoader(yaml.SafeLoader):
    """Keep ISO representations verbatim rather than YAML date coercion."""
    yaml_implicit_resolvers = {
        key: [(tag, pattern) for tag, pattern in values
              if tag != "tag:yaml.org,2002:timestamp"]
        for key, values in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }

    def construct_mapping(self, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ValueError("duplicate or non-string metadata key")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def frontmatter(content: str) -> dict:
    parts = content.lstrip("\ufeff").split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        return {}
    value = yaml.load(parts[1], Loader=MetadataLoader)
    if not isinstance(value, dict):
        raise ValueError("invalid metadata")
    return value


def aware_time(value) -> str | None:
    try:
        parsed = datetime.fromisoformat(str(value))
        return str(value) if parsed.utcoffset() is not None else None
    except (ValueError, TypeError):
        return None


def project_source(session: Session, root: Path, meta: dict, content: str,
                   now: str) -> tuple[str | None, str, str]:
    public_id = meta.get("id", meta.get("source_id"))
    if meta.get("snapshot_id") and not meta.get("title"):
        return None, "archived", "来源快照原件；未转换为独立来源。"
    if not isinstance(public_id, str) or not re.fullmatch(r"SRC-\d{4,}", public_id):
        return None, "archived", "保留原件；没有可识别的来源编号。"
    number = int(public_id[4:])
    if session.get(Source, number) or session.scalar(select(Source).where(Source.public_id == public_id)):
        return public_id, "review", "来源编号已存在；未覆盖数据库，请对照原件核对。"
    values = {key: meta[key] for key in SourceCreate.model_fields if key in meta and key != "propositions"}
    values.update(kind=meta.get("source_kind", meta.get("kind", "other")),
                  original_url=meta.get("original_url", meta.get("url")))
    for key in ("creator", "publisher", "published_at"):
        if values.get(key) == "pending":
            values[key] = None
    if not values.get("creator") and isinstance(meta.get("authors"), list):
        values["creator"] = ", ".join(meta["authors"])
    values["topics"] = meta.get("topics", meta.get("classification", []))
    values["stance_as_of"] = aware_time(meta.get("stance_as_of", meta.get("as_of")))
    if values.get("published_at") is not None:
        values["published_at"] = str(values["published_at"])
    if meta.get("snapshot_record"):
        snapshot = frontmatter(data_path(root, str(meta["snapshot_record"])).read_text(encoding="utf-8"))
        if snapshot.get("source_id") != public_id or snapshot.get("snapshot_id") != meta.get("snapshot_id"):
            raise ValueError("snapshot mismatch")
        for key in ("raw_archive_path", "raw_archive_sha256", "raw_archive_bytes"):
            if key in snapshot:
                values[key] = snapshot[key]
    payload = SourceCreate.model_validate(values)
    if payload.raw_archive_path:
        raw = data_path(root, payload.raw_archive_path).read_bytes()
        if (payload.raw_archive_sha256 and hashlib.sha256(raw).hexdigest() != payload.raw_archive_sha256.lower()
                or payload.raw_archive_bytes is not None and len(raw) != payload.raw_archive_bytes):
            raise ValueError("archive checksum mismatch")
    fields = payload.model_dump(exclude={"propositions"})
    for key in ("original_url", "canonical_url", "stance_as_of"):
        if fields[key] is not None:
            fields[key] = str(fields[key])
    original_time = aware_time(meta.get("recorded_at", meta.get("created_at")))
    source = Source(id=number, public_id=public_id, created_at=original_time or now, **fields)
    # Only an explicitly attributed table is adapted, never prose or user stance.
    section = re.search(r"^## 原作者命题\s*\n(.*?)(?=^## |\Z)", content, re.M | re.S)
    if section and "协作者归纳" in section[1]:
        seen = set()
        for match in re.finditer(r"^\|\s*`?(SRC-\d{4,}/P(\d{2,}))`?\s*\|([^|]+)\|", section[1], re.M):
            if not match[1].startswith(public_id + "/") or match[2] in seen:
                raise ValueError("invalid proposition identifiers")
            seen.add(match[2])
            source.propositions.append(SourceProposition(public_id=match[1], ordinal=int(match[2]),
                text=match[3].strip(), attribution="collaborator_summary", created_at=original_time or now))
    session.add(source)
    session.flush()
    note = "来源已适配；原有立场仅保留为摘要，没有生成个人回应事件。"
    if not original_time:
        note += "原录入时间未知；来源登记时间为本次导入时间，不代表思想发生时间。"
    return public_id, "imported", note


def import_legacy_files(session: Session, root: Path) -> int:
    count = 0
    for category in ("sources", "materials", "inbox", "responses", "decisions", "thought-maps", "drafts"):
        directory = data_path(root, category)
        for candidate in sorted(directory.rglob("*.md")):
            if candidate.stem.upper() in {"INDEX", "README"}:
                continue
            key = candidate.relative_to(root).as_posix()
            try:
                raw = data_path(root, key).read_bytes()
                content = raw.decode("utf-8")
            except (OSError, ValueError, UnicodeError):
                # Escaping links and non-UTF-8 files are not read or projected.
                continue
            digest = hashlib.sha256(raw).hexdigest()
            if session.scalar(select(LegacyDocument.id).where(
                    LegacyDocument.relative_key == key, LegacyDocument.sha256 == digest)):
                continue
            now = now_in_default_timezone()
            source_id, status, note = None, "archived", "保留旧文件原件，尚未转换为当前领域记录。"
            try:
                with session.begin_nested():
                    meta = frontmatter(content)
                    if category == "sources":
                        source_id, status, note = project_source(session, root, meta, content, now.isoformat())
            except (ValueError, TypeError, OSError, yaml.YAMLError, ValidationError, IntegrityError):
                source_id, status, note = None, "review", "字段、文件引用或校验值不兼容；原件已保留，需人工核对。"
            session.add(LegacyDocument(relative_key=key, sha256=digest, content=content,
                category=category, source_id=source_id, status=status, note=note,
                recorded_at=now.isoformat(), recorded_at_epoch_ms=int(now.timestamp() * 1000)))
            session.commit()
            count += 1
    return count
