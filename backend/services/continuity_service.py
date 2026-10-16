"""Mongo-compatible persistence operations for AMRHZ task continuity.

Callers must pass actor IDs obtained from a verified authentication layer.
This module deliberately does not expose HTTP routes or perform authentication.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import ValidationError

from .continuity_models import TaskCreate, TaskEvent, TaskRecord, TaskStatus


class ContinuityError(Exception):
    """Base error for continuity service operations."""


class TaskNotFound(ContinuityError):
    pass


class RevisionConflict(ContinuityError):
    pass


class InvalidTransition(ContinuityError):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _event(event_type: str, actor_id: str, revision: int, details: Dict[str, Any]) -> Dict[str, Any]:
    return TaskEvent(
        event_type=event_type,
        actor_id=actor_id,
        revision=revision,
        details=details,
    ).model_dump(mode="json")


async def create_task(collection: Any, payload: TaskCreate, actor_id: str) -> TaskRecord:
    """Create an OPEN task. actor_id must come from trusted authentication."""
    if not actor_id or not actor_id.strip():
        raise ValueError("actor_id must be a non-empty authenticated identity")
    now = _now()
    record = TaskRecord(
        title=payload.title,
        original_instruction=payload.original_instruction,
        summary=payload.summary,
        next_action=payload.next_action,
        environment=payload.environment,
        base_commit=payload.base_commit,
        evidence=payload.evidence,
        evidence_status=payload.evidence_status,
        created_by=actor_id,
        updated_by=actor_id,
        created_at=now,
        updated_at=now,
        events=[TaskEvent(
            event_type="task.created",
            actor_id=actor_id,
            revision=1,
            details={"status": TaskStatus.OPEN.value},
        )],
    )
    document = record.model_dump(by_alias=True, mode="json")
    await collection.insert_one(document)
    return record


async def get_task(collection: Any, task_id: str) -> Optional[TaskRecord]:
    document = await collection.find_one({"_id": task_id})
    if document is None:
        return None
    return TaskRecord.model_validate(document)


async def _transition(
    collection: Any,
    task_id: str,
    expected_revision: int,
    actor_id: str,
    event_type: str,
    details: Dict[str, Any],
    set_fields: Dict[str, Any],
    allowed_statuses: list[str],
) -> TaskRecord:
    if not actor_id or not actor_id.strip():
        raise ValueError("actor_id must be a non-empty authenticated identity")
    if expected_revision < 1:
        raise ValueError("expected_revision must be >= 1")

    now = _now()
    next_revision = expected_revision + 1
    update_fields = {
        **set_fields,
        "revision": next_revision,
        "updated_at": now.isoformat(),
        "updated_by": actor_id,
    }
    event = _event(event_type, actor_id, next_revision, details)
    result = await collection.update_one(
        {
            "_id": task_id,
            "revision": expected_revision,
            "status": {"$in": allowed_statuses},
        },
        {"$set": update_fields, "$push": {"events": event}},
    )
    if getattr(result, "matched_count", 0) != 1:
        existing = await collection.find_one({"_id": task_id}, {"_id": 1, "revision": 1, "status": 1})
        if existing is None:
            raise TaskNotFound(task_id)
        raise RevisionConflict(
            f"task state changed or transition is not allowed: "
            f"expected revision {expected_revision}, actual revision {existing.get('revision')}, "
            f"status {existing.get('status')}"
        )
    record = await get_task(collection, task_id)
    if record is None:
        raise TaskNotFound(task_id)
    return record


async def acknowledge_task(
    collection: Any, task_id: str, expected_revision: int, agent_id: str
) -> TaskRecord:
    """Claim an OPEN task, or accept a handoff explicitly addressed to this agent."""
    existing = await get_task(collection, task_id)
    if existing is None:
        raise TaskNotFound(task_id)
    if existing.status == TaskStatus.HANDOFF_PENDING:
        if existing.handoff_target_agent_id not in (None, agent_id):
            raise InvalidTransition("handoff is addressed to a different agent")
        allowed = [TaskStatus.HANDOFF_PENDING.value]
    else:
        allowed = [TaskStatus.OPEN.value]
    return await _transition(
        collection,
        task_id,
        expected_revision,
        agent_id,
        "task.acknowledged",
        {"accepted_scope": existing.original_instruction},
        {
            "status": TaskStatus.ACKNOWLEDGED.value,
            "current_agent_id": agent_id,
            "handoff_target_agent_id": None,
        },
        allowed,
    )


async def request_handoff(
    collection: Any,
    task_id: str,
    expected_revision: int,
    actor_id: str,
    recipient_agent_id: Optional[str],
    reason: str,
) -> TaskRecord:
    """Request handoff; ownership remains with sender until recipient acknowledges."""
    if not reason or not reason.strip():
        raise ValueError("handoff reason must not be blank")
    existing = await get_task(collection, task_id)
    if existing is None:
        raise TaskNotFound(task_id)
    if existing.current_agent_id != actor_id:
        raise InvalidTransition("only the current task owner may request handoff")
    return await _transition(
        collection,
        task_id,
        expected_revision,
        actor_id,
        "task.handoff_requested",
        {"recipient_agent_id": recipient_agent_id, "reason": reason.strip()},
        {
            "status": TaskStatus.HANDOFF_PENDING.value,
            "handoff_target_agent_id": recipient_agent_id,
        },
        [TaskStatus.ACKNOWLEDGED.value, TaskStatus.IN_PROGRESS.value, TaskStatus.BLOCKED.value],
    )


async def update_task_summary(
    collection: Any,
    task_id: str,
    expected_revision: int,
    actor_id: str,
    summary: str,
    next_action: Optional[str],
    status: TaskStatus,
) -> TaskRecord:
    """Versioned task update. Authentication/authorization remains the caller's duty."""
    if not summary or not summary.strip():
        raise ValueError("summary must not be blank")
    if status in (TaskStatus.OPEN, TaskStatus.ACKNOWLEDGED, TaskStatus.HANDOFF_PENDING):
        raise InvalidTransition("use the dedicated acknowledgement or handoff operation")
    existing = await get_task(collection, task_id)
    if existing is None:
        raise TaskNotFound(task_id)
    if existing.current_agent_id != actor_id:
        raise InvalidTransition("only the current task owner may update task state")
    allowed = [TaskStatus.ACKNOWLEDGED.value, TaskStatus.IN_PROGRESS.value, TaskStatus.BLOCKED.value]
    if existing.status not in [TaskStatus(value) for value in allowed]:
        raise InvalidTransition(f"cannot update task in state {existing.status.value}")
    if status == TaskStatus.CANCELLED:
        raise InvalidTransition("cancellation requires a separate human-owner operation")
    if status == TaskStatus.COMPLETED:
        if not existing.evidence:
            raise InvalidTransition("completion requires recorded evidence")
        if existing.evidence_status.value != "VERIFIED":
            raise InvalidTransition("completion requires evidence_status VERIFIED")
    return await _transition(
        collection,
        task_id,
        expected_revision,
        actor_id,
        "task.state_updated",
        {"from_status": existing.status.value, "to_status": status.value},
        {
            "status": status.value,
            "summary": summary.strip(),
            "next_action": next_action.strip() if next_action else None,
            "blocker": summary.strip() if status == TaskStatus.BLOCKED else None,
        },
        allowed,
    )
