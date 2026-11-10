import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


class TelemetryEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_type: Literal["page_view"]


def _utc_day(value: datetime) -> str:
    return value.astimezone(timezone.utc).date().isoformat()


def _require_admin(authorization: Optional[str]) -> None:
    expected = os.environ.get("AP1_ANALYTICS_ADMIN_TOKEN", "")
    if len(expected) < 32:
        raise HTTPException(
            status_code=503,
            detail="Admin analytics is not configured.",
        )

    supplied = ""
    if authorization and authorization.startswith("Bearer "):
        supplied = authorization[7:].strip()

    if not supplied or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/event", status_code=202)
async def record_telemetry_event(payload: TelemetryEvent):
    """
    Record an opt-in aggregate event. No IP, user-agent, referrer,
    account identifier, or client-supplied timestamp is stored.
    """
    try:
        from server import db

        day = _utc_day(datetime.now(timezone.utc))
        await db.site_analytics_daily.update_one(
            {"day": day},
            {
                "$inc": {"page_views": 1},
                "$setOnInsert": {"day": day},
            },
            upsert=True,
        )
        return {"success": True, "accepted": True}
    except Exception:
        raise HTTPException(status_code=503, detail="Telemetry storage unavailable")


@router.get("/public")
async def get_public_telemetry():
    """Return only coarse aggregate totals for the public homepage."""
    try:
        from server import db

        today = datetime.now(timezone.utc)
        start_day = _utc_day(today - timedelta(days=6))
        records = await db.site_analytics_daily.find(
            {"day": {"$gte": start_day}},
            {"_id": 0, "day": 1, "page_views": 1},
        ).sort("day", 1).to_list(7)
        recent_total = sum(int(row.get("page_views", 0)) for row in records)
        all_time_total = await db.site_analytics_daily.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$page_views"}}}
        ]).to_list(1)
        return {
            "success": True,
            "data": {
                "page_views_all_time": int(all_time_total[0]["total"]) if all_time_total else 0,
                "page_views_last_7_days": recent_total,
                "window_days": 7,
            },
        }
    except Exception:
        raise HTTPException(status_code=503, detail="Analytics temporarily unavailable")


@router.get("/admin")
async def get_admin_telemetry(
    authorization: Optional[str] = Header(default=None),
    days: int = Query(default=30, ge=7, le=90),
):
    """Return daily aggregate counts; requires a server-configured bearer token."""
    _require_admin(authorization)
    try:
        from server import db

        start_day = _utc_day(datetime.now(timezone.utc) - timedelta(days=days - 1))
        records = await db.site_analytics_daily.find(
            {"day": {"$gte": start_day}},
            {"_id": 0, "day": 1, "page_views": 1},
        ).sort("day", 1).to_list(days)
        return {
            "success": True,
            "data": {
                "window_days": days,
                "daily": [
                    {"day": row["day"], "page_views": int(row.get("page_views", 0))}
                    for row in records
                ],
                "page_views_in_window": sum(int(row.get("page_views", 0)) for row in records),
            },
        }
    except Exception:
        raise HTTPException(status_code=503, detail="Analytics temporarily unavailable")
