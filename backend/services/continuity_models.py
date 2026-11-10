"""Validated data contracts for AMRHZ task continuity.

This module contains no persistence or API wiring.
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TaskStatus(str, Enum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    HANDOFF_PENDING = "HANDOFF_PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class EvidenceStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PROPOSED = "PROPOSED"
    UNKNOWN = "UNKNOWN"
    CONFLICTING = "CONFLICTING"
    FAILED = "FAILED"
    FALLBACK = "FALLBACK"


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str = Field(min_length=1, max_length=80)
    locator: str = Field(min_length=1, max_length=2048)
    observed_result: str = Field(min_length=1, max_length=4000)
    observed_at: datetime = Field(default_factory=utc_now)


class TaskEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str = Field(min_length=1, max_length=80)
    actor_id: str = Field(min_length=1, max_length=200)
    timestamp: datetime = Field(default_factory=utc_now)
    revision: int = Field(ge=1)
    details: Dict[str, Any] = Field(default_factory=dict)


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=240)
    original_instruction: str = Field(min_length=1, max_length=12000)
    summary: str = Field(min_length=1, max_length=8000)
    next_action: str = Field(min_length=1, max_length=4000)
    environment: Optional[str] = Field(default=None, max_length=120)
    base_commit: Optional[str] = Field(default=None, max_length=80)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    evidence_status: EvidenceStatus = EvidenceStatus.UNKNOWN

    @field_validator("title", "original_instruction", "summary", "next_action")
    @classmethod
    def reject_blank_strings(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must not be blank")
        return value


class TaskRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    task_id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    schema_version: int = Field(default=1, ge=1)
    revision: int = Field(default=1, ge=1)
    title: str = Field(min_length=1, max_length=240)
    original_instruction: str = Field(min_length=1, max_length=12000)
    status: TaskStatus = TaskStatus.OPEN
    evidence_status: EvidenceStatus = EvidenceStatus.UNKNOWN
    current_agent_id: Optional[str] = Field(default=None, max_length=200)
    handoff_target_agent_id: Optional[str] = Field(default=None, max_length=200)
    environment: Optional[str] = Field(default=None, max_length=120)
    base_commit: Optional[str] = Field(default=None, max_length=80)
    summary: str = Field(min_length=1, max_length=8000)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    blocker: Optional[str] = Field(default=None, max_length=4000)
    next_action: Optional[str] = Field(default=None, max_length=4000)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    created_by: str = Field(min_length=1, max_length=200)
    updated_by: str = Field(min_length=1, max_length=200)
    events: List[TaskEvent] = Field(default_factory=list)

    @field_validator("title", "original_instruction", "summary", "created_by", "updated_by")
    @classmethod
    def reject_blank_strings(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must not be blank")
        return value

    @field_validator("next_action")
    @classmethod
    def terminal_action_may_be_empty(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError("next_action must be null or non-blank")
        return value
