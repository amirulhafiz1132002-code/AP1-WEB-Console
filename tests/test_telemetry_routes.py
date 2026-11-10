import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routes.telemetry_routes import create_telemetry_router


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows

    def sort(self, *_args):
        return self

    async def to_list(self, length):
        return self.rows[:length]


class FakeCollection:
    def __init__(self):
        self.rows = {}

    async def update_one(self, query, update, upsert=False):
        day = query["day"]
        self.rows.setdefault(day, {"day": day, "page_views": 0})
        self.rows[day]["page_views"] += update["$inc"]["page_views"]

    def find(self, query, projection):
        start = query["day"]["$gte"]
        rows = [
            row for day, row in sorted(self.rows.items())
            if day >= start
        ]
        return FakeCursor(rows)

    def aggregate(self, _pipeline):
        total = sum(row["page_views"] for row in self.rows.values())
        return FakeCursor([{"total": total}] if self.rows else [])


class FakeDatabase:
    def __init__(self):
        self.site_analytics_daily = FakeCollection()


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("AP1_ANALYTICS_ADMIN_TOKEN", raising=False)
    app = FastAPI()
    app.include_router(create_telemetry_router(FakeDatabase()))
    return TestClient(app)


def test_event_accepts_only_fixed_page_view_event(client):
    accepted = client.post("/telemetry/event", json={"event_type": "page_view"})
    rejected = client.post("/telemetry/event", json={"event_type": "email_capture"})

    assert accepted.status_code == 202
    assert accepted.json()["accepted"] is True
    assert rejected.status_code == 422


def test_public_summary_returns_aggregate_counts(client):
    client.post("/telemetry/event", json={"event_type": "page_view"})
    response = client.get("/telemetry/public")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["page_views_all_time"] == 1
    assert data["page_views_last_7_days"] == 1
    assert data["window_days"] == 7


def test_admin_endpoint_fails_closed_without_configuration(client):
    response = client.get("/telemetry/admin")
    assert response.status_code == 503


def test_admin_endpoint_requires_valid_bearer_token(client, monkeypatch):
    monkeypatch.setenv("AP1_ANALYTICS_ADMIN_TOKEN", "x" * 40)

    unauthorized = client.get(
        "/telemetry/admin",
        headers={"Authorization": "Bearer wrong"},
    )
    assert unauthorized.status_code == 401

    authorized = client.get(
        "/telemetry/admin",
        headers={"Authorization": "Bearer " + "x" * 40},
    )
    assert authorized.status_code == 200
    assert authorized.json()["data"]["window_days"] == 30


def test_admin_window_is_bounded(client, monkeypatch):
    monkeypatch.setenv("AP1_ANALYTICS_ADMIN_TOKEN", "y" * 40)
    response = client.get(
        "/telemetry/admin?days=365",
        headers={"Authorization": "Bearer " + "y" * 40},
    )
    assert response.status_code == 422
