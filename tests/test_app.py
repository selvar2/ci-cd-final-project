from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.notes_service import notes_service


def setup_function():
    # Reset storage for isolation
    storage_dir = Path("/tmp/cloudrun-starter")
    if storage_dir.exists():
        for path in storage_dir.glob("*"):
            path.unlink()
    notes_service._notes.clear()  # noqa: SLF001
    notes_service._sequence = 1  # noqa: SLF001


def test_health_endpoint():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_server_rendered_index():
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Notes API" in resp.text


def test_create_and_get_note():
    client = TestClient(app)
    create_resp = client.post(
        "/api/v1/notes",
        json={"title": "My Note", "content": "Hello world"},
    )
    assert create_resp.status_code == 201
    note = create_resp.json()
    assert note["title"] == "My Note"

    get_resp = client.get(f"/api/v1/notes/{note['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["content"] == "Hello world"


def test_validation_errors():
    client = TestClient(app)
    resp = client.post("/api/v1/notes", json={"title": "", "content": ""})
    assert resp.status_code == 422
    body = resp.json()
    assert "detail" in body


def test_delete_note():
    client = TestClient(app)
    create_resp = client.post(
        "/api/v1/notes",
        json={"title": "Temp", "content": "delete me"},
    )
    note_id = create_resp.json()["id"]
    delete_resp = client.delete(f"/api/v1/notes/{note_id}")
    assert delete_resp.status_code == 204
    missing_resp = client.get(f"/api/v1/notes/{note_id}")
    assert missing_resp.status_code == 404
