"""Local, append-only source capture and Docling conversion (no belief inference)."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import Request, urlopen, build_opener, HTTPRedirectHandler, ProxyHandler
from urllib.error import HTTPError
from uuid import uuid4

from .config import Settings, data_path, prepare_data_directory

MAX_BYTES = 100 * 1024 * 1024
EXTENSIONS = {'.pdf', '.html', '.htm', '.docx', '.pptx', '.xlsx', '.txt', '.md', '.png', '.jpg', '.jpeg', '.tiff'}


def stamp():
    value = datetime.now().astimezone()
    return {'recorded_at': value.isoformat(), 'recorded_at_epoch_ms': int(value.timestamp() * 1000)}


def write_json(root, key, value):
    with data_path(root, key).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def public_url(url):
    import ipaddress
    import socket
    parts = urlsplit(url)
    if parts.scheme not in {'http', 'https'} or not parts.hostname or parts.username or parts.password:
        raise ValueError('Only public HTTP(S) URLs without credentials are accepted')
    addresses = socket.getaddrinfo(parts.hostname, parts.port or (443 if parts.scheme == 'https' else 80))
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise ValueError('Private or local network URLs are not accepted by ingestion')


class PublicRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def capture(root: Path, source_id: str, snapshot: str, source: str, *, public_only=False) -> str:
    """A reserved snapshot is never reused, even after failure."""
    if not re.fullmatch(r'SRC-\d{4,}', source_id) or not re.fullmatch(r'V\d{3,}', snapshot):
        raise ValueError('Expected SRC-NNNN and VNNN')
    root = prepare_data_directory(root)
    key = f'raw/sources/{source_id}/{snapshot}'
    folder = data_path(root, key)
    folder.mkdir(parents=True, exist_ok=False)
    manifest = dict(source_id=source_id, snapshot_id=f'{source_id}/{snapshot}',
                    privacy='private', original_input=source, **stamp())
    write_json(root, f'{key}/started.json', manifest)
    try:
        is_url = urlsplit(source).scheme.lower() in ('http', 'https')
        manifest.update(captured_from='url' if is_url else 'user_provided_file',
                        accessed_at=datetime.now().astimezone().isoformat())
        if is_url:
            request = Request(source, headers={'User-Agent': 'Arrive-Archive/1.0'})
            if public_only:
                public_url(source)
                stream = build_opener(ProxyHandler({}), PublicRedirect()).open(request, timeout=30)
            else:
                stream = urlopen(request, timeout=30)
            manifest.update(final_url=stream.url, http_status=stream.status,
                            content_type=stream.headers.get_content_type(),
                            accessed_at=datetime.now().astimezone().isoformat())
            suffix = { 'text/html': '.html', 'application/pdf': '.pdf',
                       'text/plain': '.txt' }.get(stream.headers.get_content_type(),
                                                 Path(urlsplit(stream.url).path).suffix.lower())
        else:
            path = Path(source).expanduser()
            suffix = path.suffix.lower()
            stream = path.open('rb')
        with stream:
            if suffix not in EXTENSIONS:
                raise ValueError('Unsupported format; original input was not converted')
            raw_key = f'{key}/original{suffix}'
            digest = hashlib.sha256()
            size = 0
            with data_path(root, raw_key).open('xb') as out:
                while chunk := stream.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise ValueError('Input exceeds 100 MiB; partial bytes are not a complete snapshot')
                    out.write(chunk)
                    digest.update(chunk)
        manifest.update(capture_status='captured', captured_at=datetime.now().astimezone().isoformat(),
                        captured_from='url' if is_url else 'user_provided_file',
                        raw_archive_path=raw_key, raw_archive_bytes=size,
                        raw_archive_sha256=digest.hexdigest())
    except Exception as exc:
        if isinstance(exc, HTTPError):
            manifest.update(http_status=exc.code, final_url=exc.url)
        manifest.update(capture_status='failed', error_type=type(exc).__name__, error=str(exc))
        write_json(root, f'{key}/capture.json', manifest)
        raise
    write_json(root, f'{key}/capture.json', manifest)
    return f'{key}/capture.json'


def docling_convert(path: Path, artifacts: Path | None = None):
    if path.suffix.lower() in {'.txt', '.md'}:
        content = path.read_text(encoding='utf-8-sig')
        return content, {'text': content}, 'success', 'utf8-identity'
    from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    options = PdfPipelineOptions(enable_remote_services=False, do_ocr=True,
                                 ocr_options=RapidOcrOptions(lang=['ch']))
    if artifacts:
        options.artifacts_path = artifacts
    converter = DocumentConverter(format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=options, backend=PyPdfiumDocumentBackend),
        InputFormat.IMAGE: ImageFormatOption(pipeline_options=options),
    })
    result = converter.convert(path)
    return (result.document.export_to_markdown(), result.document.export_to_dict(),
            result.status.value, version('docling-slim'))


def extract(root: Path, manifest_key: str, *, converter=docling_convert,
            artifacts: Path | None = None) -> str:
    root = prepare_data_directory(root)
    manifest = json.loads(data_path(root, manifest_key).read_text(encoding='utf-8'))
    if manifest['capture_status'] != 'captured':
        raise ValueError('Cannot convert an incomplete capture')
    snapshot = manifest['snapshot_id']
    if not re.fullmatch(r'SRC-\d{4,}/V\d{3,}', snapshot):
        raise ValueError('Invalid snapshot identifier')
    raw_key = manifest['raw_archive_path']
    if not raw_key.startswith(f'raw/sources/{snapshot}/'):
        raise ValueError('Snapshot raw path mismatch')
    raw = data_path(root, raw_key)
    if raw.stat().st_size != manifest['raw_archive_bytes'] or hashlib.sha256(raw.read_bytes()).hexdigest() != manifest['raw_archive_sha256']:
        raise ValueError('Original checksum mismatch')
    run_key = f'sources/extractions/{snapshot}/{uuid4().hex}'
    data_path(root, run_key).mkdir(parents=True, exist_ok=False)
    record = dict(snapshot_id=snapshot, raw_archive_path=raw_key,
                  raw_archive_sha256=manifest['raw_archive_sha256'], privacy='private',
                  tool='docling', review_status='pending',
                  configuration={'pdf_backend': 'pypdfium2', 'ocr': 'rapidocr',
                                 'ocr_language': 'ch', 'remote_services': False}, **stamp())
    write_json(root, f'{run_key}/started.json', record)
    try:
        markdown, structured, status, tool_version = converter(raw, artifacts)
        record.update(tool_version=tool_version, conversion_status=status)
        # Empty/partial output must remain visibly pending review.
        record['status'] = 'converted' if status == 'success' and markdown.strip() else 'needs_review'
        for filename, content in [('document.md', markdown), ('document.json', json.dumps(structured, ensure_ascii=False, indent=2))]:
            with data_path(root, f'{run_key}/{filename}').open('x', encoding='utf-8') as out:
                out.write(content)
        record.update(markdown_key=f'{run_key}/document.md', structure_key=f'{run_key}/document.json')
    except Exception as exc:
        record.update(status='failed', error_type=type(exc).__name__, error=str(exc))
    record['completed_at'] = datetime.now().astimezone().isoformat()
    write_json(root, f'{run_key}/result.json', record)
    return f'{run_key}/result.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    save = sub.add_parser('capture')
    save.add_argument('source', help='Local file or HTTP(S) URL')
    save.add_argument('--source-id', required=True)
    save.add_argument('--snapshot', required=True, help='New immutable VNNN identifier')
    save.add_argument('--capture-only', action='store_true')
    retry = sub.add_parser('extract')
    retry.add_argument('manifest', help='Data-root relative capture.json key')
    for cmd in (save, retry):
        cmd.add_argument('--artifacts-path', type=Path)
    args = parser.parse_args()
    root = Settings().data_dir
    manifest = capture(root, args.source_id, args.snapshot, args.source) if args.command == 'capture' else args.manifest
    print(manifest)
    if args.command == 'capture' and args.capture_only:
        return
    result = extract(root, manifest, artifacts=args.artifacts_path)
    print(result)
    state = json.loads(data_path(root, result).read_text(encoding='utf-8'))['status']
    if state != 'converted':
        parser.exit(1, f'Conversion status: {state}; original preserved; inspect result.json\n')


if __name__ == '__main__':
    main()
