"""Opt-in real PDF/OCR intake smoke test; synthetic files in a temporary data root.

Run with backend Python: python scripts/check_document_conversion.py
Initial Docling model downloads may require network access. No private files used.
"""
import argparse
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import time


def native_pdf(path):
    stream = b'BT /F1 18 Tf 72 700 Td (Synthetic archive verification 42) Tj ET'
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>',
               b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
               b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
               b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
               b'<< /Length ' + str(len(stream)).encode() + b' >>\nstream\n' + stream + b'\nendstream']
    output = b'%PDF-1.4\n'
    offsets = []
    for ordinal, obj in enumerate(objects, 1):
        offsets.append(len(output))
        output += f'{ordinal} 0 obj\n'.encode() + obj + b'\nendobj\n'
    start = len(output)
    output += b'xref\n0 6\n0000000000 65535 f \n'
    for offset in offsets:
        output += f'{offset:010d} 00000 n \n'.encode()
    output += f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF'.encode()
    path.write_bytes(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', type=Path, default=Path('C:/Windows/Fonts/msyh.ttc'))
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args()
    if not args.font.is_file():
        parser.error('Provide --font pointing to an installed Chinese TrueType font')
    with TemporaryDirectory(prefix='arrive-pdf-ocr-smoke-') as temp:
        base = Path(temp)
        os.environ['ARRIVE_DATA_DIR'] = str(base / 'data')
        os.environ.pop('ARRIVE_DATABASE_URL', None)
        from PIL import Image, ImageDraw, ImageFont
        from fastapi.testclient import TestClient
        from arrive.main import create_app
        from arrive.database import engine
        from arrive.config import data_path, get_settings
        import json
        text_pdf = base / 'synthetic-text.pdf'
        native_pdf(text_pdf)
        scan = base / 'synthetic-scan.pdf'
        image = Image.new('RGB', (1600, 2100), 'white')
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(str(args.font), 48)
        draw.text((120, 180), '合成文档测试', font=font, fill='black')
        draw.text((120, 300), '这是完全虚构的文字。', font=font, fill='black')
        draw.text((120, 420), 'Archive number 42', font=font, fill='black')
        image.save(scan, 'PDF', resolution=150)
        try:
            with TestClient(create_app()) as client:
                for file, expected in [(text_pdf, 'Synthetic archive verification 42'),
                                       (scan, '这是完全虚构的文字')]:
                    response = client.post('/api/v1/source-files',
                        params={'filename': file.name, 'title': 'Synthetic smoke test'},
                        content=file.read_bytes())
                    assert response.status_code == 201, response.text
                    owner = response.json()['id']
                    deadline = time.monotonic() + args.timeout
                    while time.monotonic() < deadline:
                        job = client.get(f'/api/v1/documents/{owner}').json()[0]
                        if job['status'] not in ('pending', 'running'):
                            break
                        time.sleep(.25)
                    if job['status'] != 'converted':
                        if job['result_key']:
                            print(data_path(get_settings().data_dir, job['result_key']).read_text(encoding='utf-8'), flush=True)
                        raise AssertionError(f'{file.name}: {job["status"]}: {job["error"]}')
                    markdown = client.get(f'/api/v1/documents/{owner}/{job["id"]}/markdown').text
                    assert expected in markdown, markdown
                    record = json.loads(data_path(get_settings().data_dir, job['result_key']).read_text(encoding='utf-8'))
                    document = json.loads(data_path(get_settings().data_dir, record['structure_key']).read_text(encoding='utf-8'))
                    assert any(text.get('prov') for text in document['texts']), 'Missing PDF page provenance'
                    assert data_path(get_settings().data_dir, record['raw_archive_path']).read_bytes() == file.read_bytes()
                    print(f'PASS {file.name}: automatic intake, Markdown, page provenance, original bytes', flush=True)
        finally:
            engine.dispose()


if __name__ == '__main__':
    main()
