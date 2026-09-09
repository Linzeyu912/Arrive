"""Automatic conversion worker. One local backend process owns the data root."""
import json
import hashlib
from pathlib import Path
from threading import Event, Thread
from uuid import uuid4

from sqlalchemy import select, update

from .config import data_path, prepare_data_directory
from .document_archive import capture, extract, stamp
from .models import DocumentJob, Source
from filelock import FileLock


def enqueue(session, owner_id, kind, value):
    job = DocumentJob(owner_id=owner_id, input_kind=kind, input_value=value,
                      status='pending', **stamp())
    session.add(job)
    return job


def process_one(factory, root, converter=None):
    """Persisted inputs survive conversion errors. Claim before doing slow I/O."""
    with factory() as session:
        job = session.scalar(select(DocumentJob).where(DocumentJob.status == 'pending').order_by(DocumentJob.id))
        if job is None:
            return False
        claimed = session.execute(update(DocumentJob).where(DocumentJob.id == job.id, DocumentJob.status == 'pending').values(status='running'))
        session.commit()
        if not claimed.rowcount:
            return True
        try:
            if job.input_kind == 'text':
                key = f'outputs/normalized/{job.owner_id}/{uuid4().hex}.md'
                path = data_path(root, key)
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('x', encoding='utf-8', newline='') as out:
                    out.write(job.input_value)
                job.markdown_key = key
                job.status = 'converted'
            else:
                manifest = job.manifest_key
                if not manifest or not data_path(root, manifest).exists():
                    value = str(data_path(root, job.input_value)) if job.input_kind == 'file' else job.input_value
                    if job.input_kind == 'file':
                        source = session.scalar(select(Source).where(Source.public_id == job.owner_id))
                        raw = Path(value).read_bytes()
                        if source and ((source.raw_archive_sha256 and hashlib.sha256(raw).hexdigest().lower() != source.raw_archive_sha256.lower()) or (source.raw_archive_bytes is not None and len(raw) != source.raw_archive_bytes)):
                            raise ValueError('Stored input checksum mismatch')
                    # Existing manual snapshots retain their numbering and bytes.
                    ordinal = job.id
                    while data_path(root, f'raw/sources/{job.owner_id}/V{ordinal:06d}').exists():
                        ordinal += 1
                    snapshot = f'V{ordinal:06d}'
                    job.manifest_key = f'raw/sources/{job.owner_id}/{snapshot}/capture.json'
                    session.commit()
                    manifest = capture(root, job.owner_id, snapshot, value, public_only=job.input_kind == 'url')
                job.manifest_key = manifest
                session.commit()
                kwargs = {'converter': converter} if converter else {}
                job.result_key = extract(root, manifest, **kwargs)
                result = json.loads(data_path(root, job.result_key).read_text(encoding='utf-8'))
                job.status = result['status']
                job.markdown_key = result.get('markdown_key')
                job.error = result.get('error_type')
        except Exception as exc:
            # Full failure details stay in private snapshot records where available.
            job.status = 'failed'
            job.error = type(exc).__name__
        session.commit()
    return True


class ConversionWorker:
    def __init__(self, factory, root):
        self.factory, self.root = factory, prepare_data_directory(root)
        self.stop = Event()
        self.lock = FileLock(str(data_path(self.root, 'cache/document-worker.lock')))
        self.thread = Thread(target=self.run, name='arrive-document-conversion', daemon=True)

    def start(self):
        self.lock.acquire(timeout=0)
        # Supported deployment is one backend process per data root.
        with self.factory() as session:
            session.execute(update(DocumentJob).where(DocumentJob.status == 'running').values(status='pending'))
            session.commit()
        self.thread.start()

    def run(self):
        while not self.stop.is_set():
            try:
                if process_one(self.factory, self.root):
                    continue
            except Exception:
                pass  # Transaction rollback; retry queue polling without logging user content.
            self.stop.wait(1)

    def close(self):
        self.stop.set()
        self.thread.join(timeout=2)
        if not self.thread.is_alive():
            self.lock.release()
