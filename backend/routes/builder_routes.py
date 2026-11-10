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
                "execution_status": response.get("execution_status", "unknown"),
                "model_success": response.get("success") is True and not response.get("fallback", False),
                "fallback": response.get("fallback", False),
                "result": response,
            },
        )

        model_success = response.get("success") is True and not response.get("fallback", False)
        execution_status = response.get("execution_status", "unknown")
        return {
            "success": model_success,
            "request_processed": True,
            "execution_status": execution_status,
            "message": (
                "Builder model execution completed successfully."
                if model_success
                else "Builder request processed without verified model execution."
            ),
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
    memory_dir = Path(__file__).resolve().parents[2] / "memory"
    writable = memory_dir.is_dir() and os.access(memory_dir, os.W_OK)

    return {
        "success": writable,
        "status": "ok" if writable else "degraded",
        "memory_writable": writable,
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "service": "builder",
    }
