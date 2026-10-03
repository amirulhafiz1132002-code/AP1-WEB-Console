import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from filelock import FileLock

REPO_ROOT = Path(__file__).resolve().parents[2]
MEMORY_DIR = REPO_ROOT / "memory"
EVENTS_FILE = MEMORY_DIR / "events.jsonl"


def _ensure_memory_dir() -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def append_event(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(event_type, str) or not event_type.strip():
        raise ValueError("event_type must be a non-empty string")
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dictionary")

    _ensure_memory_dir()

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "payload": payload,
    }

    lock_path = MEMORY_DIR / ".events.lock"
    with FileLock(str(lock_path)):
        with EVENTS_FILE.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    return entry


def get_recent_events(limit: int = 50) -> List[Dict[str, Any]]:
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("limit must be a positive integer")

    _ensure_memory_dir()

    lock_path = MEMORY_DIR / ".events.lock"
    with FileLock(str(lock_path)):
        if not EVENTS_FILE.exists():
            return []

        lines = EVENTS_FILE.read_text(encoding="utf-8").splitlines()
        records: List[Dict[str, Any]] = []
        for line in lines[-limit:]:
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return records
