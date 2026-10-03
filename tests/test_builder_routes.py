from pathlib import Path

from fastapi.testclient import TestClient

from backend.server import app

TEST_EVENTS_PATH = Path(__file__).resolve().parents[1] / "memory" / "events.jsonl"


def setup_memory_file() -> None:
    TEST_EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TEST_EVENTS_PATH.exists():
        TEST_EVENTS_PATH.unlink()
    TEST_EVENTS_PATH.touch()


def test_build_rejects_empty_or_malformed_inputs():
    client = TestClient(app)
    setup_memory_file()

    bad_payloads = [
        {},
        {"task": ""},
        {"task": 123},
        {"context": "not-a-dict"},
    ]

    for payload in bad_payloads:
        response = client.post("/api/builder/build", json=payload)
        assert response.status_code == 422


def test_valid_build_appends_state_entry():
    client = TestClient(app)
    setup_memory_file()

    payload = {
        "task": "Create a secure AI builder workflow",
        "context": {"repo": "AP1-WEB-Console", "phase": "planning"},
    }

    response = client.post("/api/builder/build", json=payload)
    assert response.status_code == 200

    lines = TEST_EVENTS_PATH.read_text(encoding="utf-8").splitlines()
    assert any('"event_type": "builder.started"' in line for line in lines)
    assert any('"event_type": "builder.completed"' in line for line in lines)


def test_get_events_reads_back_recorded_logs():
    client = TestClient(app)
    setup_memory_file()

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
