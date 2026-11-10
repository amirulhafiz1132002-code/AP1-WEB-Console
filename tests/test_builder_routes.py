import json
import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "ap1_test")
os.environ.setdefault("CORS_ORIGINS", "http://localhost")

from backend.server import app
from routes import builder_routes
from services import memory_service
from services.openai_service import openai_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def isolated_events_file(monkeypatch, tmp_path):
    test_memory_dir = tmp_path / "memory"
    test_events_file = test_memory_dir / "events.jsonl"

    monkeypatch.setattr(memory_service, "MEMORY_DIR", test_memory_dir)
    monkeypatch.setattr(memory_service, "EVENTS_FILE", test_events_file)

    return test_events_file


@pytest.fixture
def fallback_builder(monkeypatch):
    async def fake_fallback(prompt, context):
        return {
            "success": False,
            "execution_status": "fallback",
            "fallback": True,
            "model": "test-model",
            "data": {"analysis": "Local fallback used.", "confidence": 0.0},
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    monkeypatch.setattr(openai_service, "generate_builder_response", fake_fallback)


@pytest.fixture
def successful_builder(monkeypatch):
    async def fake_model_response(prompt, context):
        return {
            "success": True,
            "execution_status": "model",
            "fallback": False,
            "model": "test-model",
            "data": {"analysis": "Mocked model response.", "confidence": 0.95},
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }

    monkeypatch.setattr(openai_service, "generate_builder_response", fake_model_response)


def test_build_rejects_empty_or_malformed_inputs(client):
    bad_payloads = [
        {},
        {"task": ""},
        {"task": 123},
        {"context": "not-a-dict"},
    ]

    for payload in bad_payloads:
        response = client.post("/api/builder/build", json=payload)
        assert response.status_code == 422


def test_fallback_is_not_reported_as_model_success(
    client, isolated_events_file, fallback_builder
):
    payload = {
        "task": "Create a secure AI builder workflow",
        "context": {"repo": "AP1-WEB-Console", "phase": "testing"},
    }

    response = client.post("/api/builder/build", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["request_processed"] is True
    assert body["success"] is False
    assert body["execution_status"] == "fallback"
    assert body["data"]["fallback"] is True

    events = [
        json.loads(line)
        for line in isolated_events_file.read_text(encoding="utf-8").splitlines()
    ]
    completed = next(event for event in events if event["event_type"] == "builder.completed")
    assert completed["payload"]["execution_status"] == "fallback"
    assert completed["payload"]["model_success"] is False
    assert completed["payload"]["fallback"] is True


def test_real_model_success_is_reported_explicitly(
    client, isolated_events_file, successful_builder
):
    response = client.post(
        "/api/builder/build",
        json={"task": "Summarize repository state", "context": {}},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["request_processed"] is True
    assert body["success"] is True
    assert body["execution_status"] == "model"
    assert body["data"]["fallback"] is False

    events = [
        __import__("json").loads(line)
        for line in isolated_events_file.read_text(encoding="utf-8").splitlines()
    ]
    completed = next(event for event in events if event["event_type"] == "builder.completed")
    assert completed["payload"]["model_success"] is True
    assert completed["payload"]["execution_status"] == "model"


def test_get_events_reads_back_recorded_logs(
    client, isolated_events_file, fallback_builder
):
    post_response = client.post(
        "/api/builder/build",
        json={
            "task": "Read repository state and summarize",
            "context": {"repo": "AP1-WEB-Console", "phase": "analysis"},
        },
    )
    assert post_response.status_code == 200

    events_response = client.get("/api/builder/events")
    assert events_response.status_code == 200
    body = events_response.json()

    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 2
    assert any(event["event_type"] == "builder.started" for event in body["data"])
    assert any(
        event["event_type"] == "builder.completed"
        and event["payload"]["execution_status"] == "fallback"
        for event in body["data"]
    )


def test_health_check_is_read_only_and_reports_degraded_state(client, monkeypatch, tmp_path):
    fake_file = tmp_path / "backend" / "routes" / "builder_routes.py"
    fake_file.parent.mkdir(parents=True)
    monkeypatch.setattr(builder_routes, "__file__", str(fake_file))

    memory_dir = tmp_path / "memory"
    assert not memory_dir.exists()

    response = client.get("/api/builder/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["status"] == "degraded"
    assert body["memory_writable"] is False
    assert not memory_dir.exists()
