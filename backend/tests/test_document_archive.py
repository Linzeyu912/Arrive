import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import pytest

from arrive.document_archive import capture, extract


def fake_convert(path, artifacts):
    return '# 合成标题\n\n合成正文。', {'texts': [{'text': '合成正文。', 'prov': [{'page_no': 1}]}]}, 'success', 'synthetic-test'


def test_capture_extract_retry_and_immutable(tmp_path):
    original = tmp_path / 'synthetic.html'
    original.write_text('<h1>合成标题</h1><p>合成正文。</p>', encoding='utf-8')
    root = tmp_path / 'data'
    key = capture(root, 'SRC-9001', 'V001', str(original))
    first = extract(root, key, converter=fake_convert)
    second = extract(root, key, converter=fake_convert)
    assert first != second
    record = json.loads((root / first).read_text(encoding='utf-8'))
    assert record['status'] == 'converted'
    assert record['review_status'] == 'pending'
    assert (root / record['raw_archive_path']).read_bytes() == original.read_bytes()
    assert record['recorded_at_epoch_ms'] > 0
    with pytest.raises(FileExistsError):
        capture(root, 'SRC-9001', 'V001', str(original))
    (root / record['raw_archive_path']).write_bytes(b'changed')
    with pytest.raises(ValueError, match='checksum'):
        extract(root, key, converter=fake_convert)


def test_failure_preserves_raw_and_retry(tmp_path):
    original = tmp_path / 'synthetic.pdf'
    original.write_bytes(b'%PDF synthetic invalid fixture')
    root = tmp_path / 'data'
    key = capture(root, 'SRC-9002', 'V001', str(original))
    def fail(*args):
        raise RuntimeError('Synthetic converter failure')
    result = json.loads((root / extract(root, key, converter=fail)).read_text(encoding='utf-8'))
    assert result['status'] == 'failed'
    assert (root / result['raw_archive_path']).read_bytes() == original.read_bytes()
    assert json.loads((root / extract(root, key, converter=fake_convert)).read_text(encoding='utf-8'))['status'] == 'converted'


def test_invalid_id_and_path(tmp_path):
    with pytest.raises(ValueError):
        capture(tmp_path / 'data', '../escape', 'V001', 'missing.pdf')
    with pytest.raises(ValueError):
        extract(tmp_path / 'data', '../escape.json')


def test_http_capture_and_failure(tmp_path):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/missing':
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Synthetic article</h1>')
        def log_message(self, *args):
            pass
    server = HTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    root = tmp_path / 'data'
    try:
        url = f'http://127.0.0.1:{server.server_port}'
        key = capture(root, 'SRC-9003', 'V001', url)
        result = json.loads((root / key).read_text(encoding='utf-8'))
        assert result['http_status'] == 200
        assert result['final_url'] == url
        with pytest.raises(Exception):
            capture(root, 'SRC-9003', 'V002', url + '/missing')
        failed = json.loads((root / 'raw/sources/SRC-9003/V002/capture.json').read_text(encoding='utf-8'))
        assert failed['capture_status'] == 'failed'
        assert 'raw_archive_sha256' not in failed
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

def test_partial_and_oversize_are_not_success(tmp_path, monkeypatch):
    from arrive import document_archive
    original = tmp_path / 'synthetic.html'
    original.write_bytes(b'<p>synthetic oversized content</p>')
    root = tmp_path / 'data'
    monkeypatch.setattr(document_archive, 'MAX_BYTES', 8)
    with pytest.raises(ValueError, match='100 MiB'):
        capture(root, 'SRC-9004', 'V001', str(original))
    failed = json.loads((root / 'raw/sources/SRC-9004/V001/capture.json').read_text(encoding='utf-8'))
    assert failed['capture_status'] == 'failed'
    with pytest.raises(ValueError, match='incomplete'):
        extract(root, 'raw/sources/SRC-9004/V001/capture.json', converter=fake_convert)
    monkeypatch.setattr(document_archive, 'MAX_BYTES', 1000)
    key = capture(root, 'SRC-9004', 'V002', str(original))
    def partial(*args):
        return 'some synthetic text', {}, 'partial_success', 'synthetic-test'
    result = json.loads((root / extract(root, key, converter=partial)).read_text(encoding='utf-8'))
    assert result['status'] == 'needs_review'
