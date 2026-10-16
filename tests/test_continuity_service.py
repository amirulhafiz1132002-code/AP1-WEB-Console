"""Isolated tests for AMRHZ continuity schema and service.

Uses a tiny in-memory fake collection; never touches memory/events.jsonl or a live database.
"""
import copy
import asyncio
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from backend.services.continuity_models import TaskCreate, TaskStatus
from backend.services.continuity_service import (
    InvalidTransition,
    RevisionConflict,
    acknowledge_task,
    create_task,
    get_task,
    request_handoff,
    update_task_summary,
)


class FakeCollection:
    def __init__(self):
        self.documents = {}

    async def insert_one(self, document):
        key = document["_id"]
        if key in self.documents:
            raise AssertionError("duplicate task id")
        self.documents[key] = copy.deepcopy(document)
        return SimpleNamespace(inserted_id=key)

    async def find_one(self, query, projection=None):
        document = self.documents.get(query.get("_id"))
        if document is None:
            return None
        if projection:
            return {key: value for key, value in document.items() if key not in [
                key for key, excluded in projection.items() if excluded == 0
            ]}
        return copy.deepcopy(document)

    async def update_one(self, query, update):
        document = self.documents.get(query.get("_id"))
        if document is None or document.get("revision") != query.get("revision"):
            return SimpleNamespace(matched_count=0)
        allowed = query.get("status", {}).get("$in")
        if allowed is not None and document.get("status") not in allowed:
            return SimpleNamespace(matched_count=0)
        document.update(copy.deepcopy(update.get("$set", {})))
        for key, value in update.get("$push", {}).items():
            document.setdefault(key, []).append(copy.deepcopy(value))
        return SimpleNamespace(matched_count=1)


def payload(**overrides):
    data = {
        "title": "Continuity test",
        "original_instruction": "Create a checkpoint",
        "summary": "Schema/service test only",
        "next_action": "Verify transition",
    }
    data.update(overrides)
    return TaskCreate(**data)


def run(coro):
    return asyncio.run(coro)


def test_task_create_rejects_blank_instruction():
    with pytest.raises(ValidationError):
        payload(original_instruction="   ")


def test_create_and_read_task_starts_open_revision_one():
    collection = FakeCollection()
    record = run(create_task(collection, payload(), "human-test"))
    readback = run(get_task(collection, record.task_id))
    assert readback is not None
    assert readback.task_id == record.task_id
    assert readback.revision == 1
    assert readback.status == TaskStatus.OPEN
    assert readback.events[0].event_type == "task.created"


def test_acknowledge_claims_open_task_and_increments_revision():
    collection = FakeCollection()
    record = run(create_task(collection, payload(), "human-test"))
    claimed = run(acknowledge_task(collection, record.task_id, 1, "agent-a"))
    assert claimed.status == TaskStatus.ACKNOWLEDGED
    assert claimed.current_agent_id == "agent-a"
    assert claimed.revision == 2


def test_stale_revision_is_rejected_without_overwrite():
    collection = FakeCollection()
    record = run(create_task(collection, payload(), "human-test"))
    run(acknowledge_task(collection, record.task_id, 1, "agent-a"))
    before = run(get_task(collection, record.task_id))
    with pytest.raises(RevisionConflict):
        run(acknowledge_task(collection, record.task_id, 1, "agent-b"))
    after = run(get_task(collection, record.task_id))
    assert after.revision == before.revision
    assert after.current_agent_id == "agent-a"


def test_handoff_keeps_sender_until_recipient_acknowledges():
    collection = FakeCollection()
    record = run(create_task(collection, payload(), "human-test"))
    claimed = run(acknowledge_task(collection, record.task_id, 1, "agent-a"))
    handoff = run(request_handoff(
        collection, record.task_id, claimed.revision, "agent-a", "agent-b", "Switch environment"
    ))
    assert handoff.status == TaskStatus.HANDOFF_PENDING
    assert handoff.current_agent_id == "agent-a"
    assert handoff.handoff_target_agent_id == "agent-b"
    accepted = run(acknowledge_task(collection, record.task_id, handoff.revision, "agent-b"))
    assert accepted.status == TaskStatus.ACKNOWLEDGED
    assert accepted.current_agent_id == "agent-b"
    assert accepted.handoff_target_agent_id is None


def test_handoff_target_mismatch_is_rejected():
    collection = FakeCollection()
    record = run(create_task(collection, payload(), "human-test"))
    claimed = run(acknowledge_task(collection, record.task_id, 1, "agent-a"))
    handoff = run(request_handoff(
        collection, record.task_id, claimed.revision, "agent-a", "agent-b", "Switch environment"
    ))
    with pytest.raises(InvalidTransition):
        run(acknowledge_task(collection, record.task_id, handoff.revision, "agent-c"))


def test_completion_requires_evidence():
    collection = FakeCollection()
    record = run(create_task(collection, payload(), "human-test"))
    claimed = run(acknowledge_task(collection, record.task_id, 1, "agent-a"))
    with pytest.raises(InvalidTransition):
        run(update_task_summary(
            collection, record.task_id, claimed.revision, "agent-a",
            "Claimed complete", None, TaskStatus.COMPLETED
        ))


def test_completion_rejects_evidence_marked_unknown():
    from backend.services.continuity_models import EvidenceItem, EvidenceStatus

    collection = FakeCollection()
    record = run(create_task(collection, payload(
        evidence=[EvidenceItem(
            kind="test",
            locator="local-test",
            observed_result="A test result exists but is not verified",
        )],
        evidence_status=EvidenceStatus.UNKNOWN,
    ), "human-test"))
    claimed = run(acknowledge_task(collection, record.task_id, 1, "agent-a"))
    with pytest.raises(InvalidTransition):
        run(update_task_summary(
            collection, record.task_id, claimed.revision, "agent-a",
            "Claimed complete", None, TaskStatus.COMPLETED
        ))
