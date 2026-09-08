"""Build and verify Compose with synthetic records in an isolated temp data root."""
from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import urllib.error
import urllib.request
from uuid import uuid4


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data = Path(tempfile.mkdtemp(prefix="arrive-docker-test-"))
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    env = os.environ.copy()
    env.update(ARRIVE_DOCKER_DATA_DIR=str(data), ARRIVE_PORT=str(port))
    project = "arrive-test-" + uuid4().hex[:10]
    command = ["docker", "compose", "-p", project, "-f", str(root / "compose.yaml")]

    def compose(*args: str) -> None:
        subprocess.run(command + list(args), cwd=root, env=env, check=True)

    def request(path: str, payload: dict | None = None):
        body = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}{path}", data=body,
            headers={"Content-Type": "application/json"} if body else {},
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.status, response.read()

    try:
        compose("up", "--build", "-d", "--wait", "--wait-timeout", "180")
        assert json.loads(request("/health")[1])["status"] == "ok"
        assert b'<div id="root"' in request("/materials/M001")[1]
        status, content = request("/api/v1/materials", {
            "content": "SYNTHETIC Docker verification\nPreserve this newline.",
            "preserve_verbatim": True,
        })
        assert status == 201
        material = json.loads(content)
        status, content = request("/api/v1/sources", {
            "kind": "web_article", "title": "SYNTHETIC source",
            "original_url": "https://example.com/docker-test",
            "propositions": [{"text": "SYNTHETIC proposition", "attribution": "author_explicit"}],
        })
        assert status == 201
        target = json.loads(content)["propositions"][0]["id"]
        status, content = request("/api/v1/responses", {
            "target_id": target, "resonance": "high", "agreement": "uncertain",
            "adoption": "adapt", "creates_personal_proposition_text": "SYNTHETIC personal proposition",
        })
        assert status == 201 and json.loads(content)["creates_personal_proposition_id"]
        from urllib.parse import quote
        snapshot = json.loads(request("/api/v1/responses/snapshot/" + quote(target, safe=""))[1])
        assert snapshot["agreement"]["value"] == "uncertain"
        try:
            request("/api/v1/not-a-route")
        except urllib.error.HTTPError as error:
            assert error.code == 404 and "detail" in json.loads(error.read())
        else:
            raise AssertionError("API errors must not fall back to index.html")
        compose("down")
        compose("up", "-d", "--wait", "--wait-timeout", "180")
        records = json.loads(request("/api/v1/materials")[1])
        assert any(item["id"] == material["id"] and item["content"] == material["content"] for item in records)
        compose("exec", "-T", "api", "python", "-c",
                "import sqlite3; c=sqlite3.connect('/data/database/arrive.db'); "
                "assert c.execute('select version_num from alembic_version').fetchone()")
        print("Docker smoke passed: SPA, API, adoption, migrations, and persistence.")
    finally:
        subprocess.run(command + ["down", "--remove-orphans"], cwd=root, env=env, check=False)
        # Keep only this synthetic temp directory for diagnosis; never remove user data.
        print(f"Synthetic test data retained at: {data}")


if __name__ == "__main__":
    main()
