import json
from types import SimpleNamespace

import pytest
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from arrive.config import prepare_data_directory
from arrive.database import get_session
from arrive.ingestion import process_one, enqueue, ConversionWorker
from arrive.models import DocumentJob
from arrive import config


def setup(client, tmp_path, monkeypatch):
    root = prepare_data_directory(tmp_path / 'data')
    monkeypatch.setattr(config, 'get_settings', lambda: SimpleNamespace(data_dir=root))
    generator = client.app.dependency_overrides[get_session]()
    session = next(generator)
    factory = sessionmaker(bind=session.get_bind(), expire_on_commit=False)
    session.close()
    return root, factory


def test_file_intake_automatically_queues_and_saves_md(client, tmp_path, monkeypatch):
    root, factory = setup(client, tmp_path, monkeypatch)
    content = '合成外部文件。\n不是个人观点。'
    response = client.post('/api/v1/source-files?filename=synthetic.txt&title=synthetic', content=content.encode())
    assert response.status_code == 201, response.text
    source = response.json()
    assert source['original_url'] is None
    assert (root / source['raw_archive_path']).read_bytes() == content.encode()
    records = client.get('/api/v1/documents/' + source['id']).json()
    assert records[0]['status'] == 'pending'
    assert process_one(factory, root)
    result = client.get('/api/v1/documents/' + source['id']).json()[0]
    assert result['status'] == 'converted'
    assert client.get(f"/api/v1/documents/{source['id']}/{result['id']}/markdown").text == content
    assert client.get('/api/v1/materials').json() == []
    assert not process_one(factory, root)


def test_text_input_is_preserved_and_queued(client, tmp_path, monkeypatch):
    root, factory = setup(client, tmp_path, monkeypatch)
    content = '  完全合成输入\r\n\n保留空白  '
    result = client.post('/api/v1/materials', json={'kind':'thought','content':content,'recorded_at':'2026-09-09T10:00:00+08:00'})
    assert result.status_code == 201, result.text
    assert process_one(factory, root)
    with factory() as session:
        job = session.scalar(select(DocumentJob))
        assert (root/job.markdown_key).read_bytes() == content.encode()


def test_url_is_queued_without_request_time_network(client, tmp_path, monkeypatch):
    root, factory = setup(client, tmp_path, monkeypatch)
    response = client.post('/api/v1/sources', json={'kind':'web_article','title':'Synthetic URL','original_url':'https://example.org/synthetic'})
    assert response.status_code == 201
    with factory() as session:
        job = session.scalar(select(DocumentJob))
        assert job.input_kind == 'url' and job.status == 'pending'


def test_worker_failure_does_not_lose_intake(client, tmp_path, monkeypatch):
    root, factory = setup(client, tmp_path, monkeypatch)
    response = client.post('/api/v1/source-files?filename=synthetic.pdf&title=synthetic',content=b'%PDF synthetic')
    assert response.status_code == 201
    def fail(*args):
        raise RuntimeError('Synthetic failure')
    assert process_one(factory, root, converter=fail)
    with factory() as session:
        job = session.scalar(select(DocumentJob))
        assert job.status == 'failed'
        record=json.loads((root/job.manifest_key).read_text(encoding='utf-8'))
        assert (root/record['raw_archive_path']).read_bytes() == b'%PDF synthetic'
    assert client.get('/api/v1/sources/' + response.json()['id']).status_code == 200


def test_worker_resumes_interrupted_job_and_excludes_second_worker(client, tmp_path, monkeypatch):
    from filelock import Timeout
    root, factory = setup(client, tmp_path, monkeypatch)
    with factory() as session:
        job = enqueue(session,'M900','text','synthetic restart')
        job.status='running'
        session.commit()
    worker = ConversionWorker(factory, root)
    # Keep the thread paused so recovery status is deterministic.
    monkeypatch.setattr(worker.thread,'start',lambda:None)
    worker.start()
    try:
        with factory() as session:
            assert session.scalar(select(DocumentJob.status)) == 'pending'
        with pytest.raises(Timeout):
            ConversionWorker(factory, root).start()
        assert process_one(factory, root)
    finally:
        worker.lock.release()


def test_private_network_input_fails_in_background(client,tmp_path,monkeypatch):
    root,factory=setup(client,tmp_path,monkeypatch)
    result=client.post('/api/v1/sources',json={'kind':'web_article','title':'Synthetic private address','original_url':'http://127.0.0.1/synthetic'})
    assert result.status_code==201
    assert process_one(factory,root)
    with factory() as session:
        assert session.scalar(select(DocumentJob.status))=='failed'
