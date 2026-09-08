"""All documents below are fully synthetic fixtures."""
import hashlib
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from arrive.config import prepare_data_directory
from arrive.database import run_migrations, build_engine
from arrive.legacy_import import import_legacy_files
from arrive.models import LegacyDocument, Source, Material, ResponseEvent


def setup(tmp_path):
    root = tmp_path / "data"
    prepare_data_directory(root)
    url = f"sqlite:///{(root / 'database' / 'test.db').as_posix()}"
    run_migrations(url)
    return root, build_engine(url)


CARD = '''---
id: SRC-0090
source_kind: web_article
original_url: https://example.com/synthetic-only
title: 完全虚构的测试来源
creator: pending
accessed_at: 2020-01-01
---
## 原作者命题
| 命题 ID | 协作者归纳 | 使用者状态 |
| --- | --- | --- |
| `SRC-0090/P03` | 完全虚构的测试命题。 | 待确认 |
'''


def test_repeat_import_and_changed_file_never_overwrite(tmp_path):
    root, engine = setup(tmp_path)
    path = root / "sources" / "synthetic.md"
    path.write_text(CARD, encoding="utf-8")
    with Session(engine) as session:
        assert import_legacy_files(session, root) == 1
        assert import_legacy_files(session, root) == 0
        source = session.get(Source, 90)
        assert source.public_id == "SRC-0090"
        assert source.creator is None
        assert source.created_at != "2020-01-01"
        assert source.propositions[0].public_id == "SRC-0090/P03"
        assert source.propositions[0].attribution == "collaborator_summary"
        assert "原录入时间未知" in session.scalar(select(LegacyDocument)).note
        path.write_text(CARD.replace("完全虚构的测试来源", "完全虚构的更新标题"), encoding="utf-8")
        assert import_legacy_files(session, root) == 1
        session.expire_all()
        assert session.get(Source, 90).title == "完全虚构的测试来源"
        assert session.scalar(select(LegacyDocument).order_by(LegacyDocument.id.desc())).status == "review"
        assert session.scalar(select(func.count()).select_from(Source)) == 1
        assert session.scalar(select(func.count()).select_from(LegacyDocument)) == 2
    engine.dispose()


def test_snapshot_aliases_and_non_domain_archives(tmp_path):
    root, engine = setup(tmp_path)
    raw = b"fully synthetic archive"
    (root / "raw" / "synthetic.txt").write_bytes(raw)
    (root / "sources" / "snapshot.md").write_text(f'''---
source_id: SRC-0091
snapshot_id: SRC-0091/V001
raw_archive_path: raw/synthetic.txt
raw_archive_sha256: {hashlib.sha256(raw).hexdigest()}
raw_archive_bytes: {len(raw)}
---
Synthetic snapshot
''', encoding="utf-8")
    (root / "sources" / "card.md").write_text('''---
source_id: SRC-0091
source_kind: other
title: Synthetic source
url: https://example.com/synthetic
authors: [Synthetic Author]
recorded_at: 2020-01-01T12:00:00+08:00
snapshot_record: sources/snapshot.md
snapshot_id: SRC-0091/V001
---
Synthetic notes
''', encoding="utf-8")
    (root / "responses" / "empty.md").write_text("---\nevent_count: 0\n---\nSynthetic empty timeline", encoding="utf-8")
    (root / "decisions" / "synthetic.md").write_text("Synthetic decision", encoding="utf-8")
    with Session(engine) as session:
        assert import_legacy_files(session, root) == 4
        source = session.get(Source, 91)
        assert source.creator == "Synthetic Author"
        assert source.created_at == "2020-01-01T12:00:00+08:00"
        assert source.raw_archive_path == "raw/synthetic.txt"
        assert session.scalar(select(func.count()).select_from(Source)) == 1
        assert session.scalar(select(func.count()).select_from(Material)) == 0
        assert session.scalar(select(func.count()).select_from(ResponseEvent)) == 0
    engine.dispose()


def test_invalid_fields_and_escaping_raw_reference_are_archived(tmp_path):
    root, engine = setup(tmp_path)
    (root / "sources" / "invalid.md").write_text(CARD.replace("---\n##", "raw_archive_path: ../outside.txt\n---\n##"), encoding="utf-8")
    (root / "sources" / "broken.md").write_text("---\ntitle: [\n---\nSynthetic", encoding="utf-8")
    with Session(engine) as session:
        assert import_legacy_files(session, root) == 2
        assert session.scalar(select(func.count()).select_from(Source)) == 0
        assert all(row.status == "review" for row in session.scalars(select(LegacyDocument)))
    engine.dispose()


def test_local_archive_api_is_read_only_and_handles_missing(client):
    assert client.get("/api/v1/local-records").json() == []
    assert client.get("/api/v1/local-records/999").status_code == 404
    assert client.post("/api/v1/local-records", json={}).status_code == 405
