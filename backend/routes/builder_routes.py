import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from services.memory_service import append_event, get_recent_events
from services.openai_service import openai_service

logger = logging.getLogger(__name__)

# This router is nested under api_router(prefix="/api") in server.py.
router = APIRouter(prefix="/builder", tags=["builder"])


class BuildRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: str = Field(..., min_length=1, description="Task to execute")
    context: Dict[str, Any] = Field(default_factory=dict)
    repository: Optional[str] = None
    priority: Optional[str] = None


@router.post("/build")
async def build_builder_task(payload: BuildRequest):
    try:
        append_event(
            "builder.started",
            {
                "task": payload.task,
                "repository": payload.repository,
                "priority": payload.priority,
                "context": payload.context,
            },
        )

        response = await openai_service.generate_builder_response(payload.task, payload.context)

        append_event(
            "builder.completed",
            {
                "task": payload.task,
                "repository": payload.repository,
                "priority": payload.priority,
                "result": response,
            },
        )

        return {
            "success": True,
            "message": "Builder task processed successfully.",
            "data": response,
        }

    except ValueError as exc:
        logger.warning("Builder validation error: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    except Exception as exc:
        logger.exception("Builder task execution failed")
        append_event(
            "builder.failed",
            {
                "task": payload.task,
                "repository": payload.repository,
                "priority": payload.priority,
                "error": str(exc),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Builder execution failed: {exc}",
        ) from exc


@router.get("/events")
async def get_builder_events(limit: int = 50):
    try:
        events = get_recent_events(limit=limit)
        return {"success": True, "count": len(events), "data": events}
    except Exception as exc:
        logger.exception("Builder events fetch failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("/health")
async def builder_health():
    memory_path = Path(__file__).resolve().parents[2] / "memory" / "events.jsonl"
    writable = False
    try:
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        with open(memory_path, "a", encoding="utf-8") as handle:
            handle.write("")
        writable = True
    except Exception as exc:
        logger.warning("Memory write check failed: %s", exc)
        writable = False

    return {
        "success": True,
        "status": "ok",
        "memory_writable": writable,
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "service": "builder",
    }
