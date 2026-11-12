import pytest
from fastapi.testclient import TestClient

from backend.server import app
from services import memory_service


@pytest.fixture
def isolated_events_file(monkeypatch, tmp_path):
    test_memory_dir = tmp_path / "memory"
    test_events_file = test_memory_dir / "events.jsonl"

    monkeypatch.setattr(memory_service, "MEMORY_DIR", test_memory_dir)
    monkeypatch.setattr(memory_service, "EVENTS_FILE", test_events_file)

    return test_events_file


def test_build_rejects_empty_or_malformed_inputs():
    client = TestClient(app)

    bad_payloads = [
        {},
        {"task": ""},
        {"task": 123},
        {"context": "not-a-dict"},
    ]

    for payload in bad_payloads:
        response = client.post("/api/builder/build", json=payload)
        assert response.status_code == 422


def test_valid_build_appends_state_entry(isolated_events_file):
    client = TestClient(app)

    payload = {
        "task": "Create a secure AI builder workflow",
        "context": {"repo": "AP1-WEB-Console", "phase": "planning"},
    }

    response = client.post("/api/builder/build", json=payload)
    assert response.status_code == 200

    lines = isolated_events_file.read_text(encoding="utf-8").splitlines()
    assert any('"event_type": "builder.started"' in line for line in lines)
    assert any('"event_type": "builder.completed"' in line for line in lines)


def test_get_events_reads_back_recorded_logs(isolated_events_file):
    client = TestClient(app)

    payload = {
        "task": "Read repository state and summarize",
        "context": {"repo": "AP1-WEB-Console", "phase": "analysis"},
    }

    post_response = client.post("/api/builder/build", json=payload)
    assert post_response.status_code == 200

    events_response = client.get("/api/builder/events")
    assert events_response.status_code == 200
    body = events_response.json()

    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 2
    assert any(event["event_type"] == "builder.started" for event in body["data"])
    assert any(event["event_type"] == "builder.completed" for event in body["data"])
