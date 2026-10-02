"""
P0 Core Tests — Critical Runtime & Core Behavior

This module contains only P0 tests as identified in TASK 004A.
These tests verify:
1. FastAPI application startup/import
2. GET /api/ root endpoint
3. POST /api/status (create status check)
4. GET /api/status (retrieve status checks)
5. Pydantic schema validation

All tests use deterministic mocks. No external API calls. No MongoDB connection.
"""

import pytest
import sys
import os
from pathlib import Path
from unittest import mock
from datetime import datetime, timezone
from pydantic import ValidationError

# Ensure backend is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_env(monkeypatch):
    """Set required environment variables for backend import."""
    monkeypatch.setenv("MONGO_URL", "mongodb://mock:mock@localhost:27017")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("CORS_ORIGINS", "*")


@pytest.fixture
def mock_motor_client(mock_env, monkeypatch):
    """Mock motor.motor_asyncio.AsyncIOMotorClient."""
    mock_client = mock.AsyncMock()
    mock_db = mock.AsyncMock()
    mock_collection = mock.AsyncMock()
    
    # Setup the mock chain: client[db_name] -> db.collection_name
    mock_client.__getitem__.return_value = mock_db
    mock_db.status_checks = mock_collection
    
    # Mock insert_one and find
    mock_collection.insert_one = mock.AsyncMock()
    mock_collection.find.return_value.to_list = mock.AsyncMock(return_value=[])
    
    # Patch motor.motor_asyncio.AsyncIOMotorClient
    monkeypatch.setattr(
        "motor.motor_asyncio.AsyncIOMotorClient",
        mock.Mock(return_value=mock_client)
    )
    
    return mock_client, mock_db, mock_collection


@pytest.fixture
def mock_github_routes(mock_env, monkeypatch):
    """Mock the GitHub routes import to avoid dependency."""
    mock_router = mock.Mock()
    mock_router.routes = []
    
    monkeypatch.setattr(
        "backend.server.github_router",
        mock_router,
        raising=False
    )


@pytest.fixture
def app_and_client(mock_env, mock_motor_client, mock_github_routes):
    """Import and initialize FastAPI app with mocked dependencies."""
    # Import the backend module (this triggers app creation)
    from backend.server import app
    
    # Create test client
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    return app, client, mock_motor_client


# ============================================================================
# P0.1: Application Startup (Verify app imports and initializes)
# ============================================================================

class TestApplicationStartup:
    """Test FastAPI application startup and initialization."""
    
    def test_app_imports_successfully(self, mock_env, mock_motor_client, mock_github_routes):
        """Verify backend.server.app can be imported without error."""
        # Should not raise any exception
        from backend.server import app
        assert app is not None
        assert hasattr(app, "routes")
    
    def test_app_title_and_version(self, app_and_client):
        """Verify FastAPI app has correct title and version."""
        app, _, _ = app_and_client
        assert app.title == "AMRHZ Portfolio API"
        assert app.version == "1.0.0"
    
    def test_api_router_configured(self, app_and_client):
        """Verify API router with /api prefix is configured."""
        app, _, _ = app_and_client
        # Check that routes include the /api prefix
        route_paths = [route.path for route in app.routes]
        # Root endpoint should be /api/
        assert "/api/" in route_paths or "/api/status" in route_paths
    
    def test_cors_middleware_attached(self, app_and_client):
        """Verify CORS middleware is attached to app."""
        app, _, _ = app_and_client
        # Check that CORSMiddleware is in the middleware stack
        middleware_types = [type(m.cls).__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_types


# ============================================================================
# P0.2: GET /api/ Root Endpoint
# ============================================================================

class TestRootEndpoint:
    """Test GET /api/ root endpoint."""
    
    def test_root_endpoint_returns_200(self, app_and_client):
        """Verify GET /api/ returns status 200."""
        _, client, _ = app_and_client
        response = client.get("/api/")
        assert response.status_code == 200
    
    def test_root_endpoint_returns_hello_world_message(self, app_and_client):
        """Verify GET /api/ returns correct message."""
        _, client, _ = app_and_client
        response = client.get("/api/")
        json_data = response.json()
        assert "message" in json_data
        assert json_data["message"] == "Hello World"
    
    def test_root_endpoint_content_type(self, app_and_client):
        """Verify GET /api/ returns JSON content type."""
        _, client, _ = app_and_client
        response = client.get("/api/")
        assert response.headers["content-type"] == "application/json"


# ============================================================================
# P0.3: POST /api/status (Create Status Check)
# ============================================================================

class TestStatusPostEndpoint:
    """Test POST /api/status endpoint."""
    
    def test_post_status_returns_201_or_200(self, app_and_client):
        """Verify POST /api/status returns 200 (FastAPI default for non-explicit status)."""
        _, client, mock_deps = app_and_client
        mock_client, mock_db, mock_collection = mock_deps
        
        payload = {"client_name": "test_client"}
        response = client.post("/api/status", json=payload)
        
        # FastAPI returns 200 by default unless explicitly set otherwise
        assert response.status_code == 200
    
    def test_post_status_accepts_client_name(self, app_and_client):
        """Verify POST /api/status accepts client_name."""
        _, client, _ = app_and_client
        payload = {"client_name": "test_client"}
        response = client.post("/api/status", json=payload)
        assert response.status_code == 200
    
    def test_post_status_returns_status_check_response(self, app_and_client):
        """Verify POST /api/status returns StatusCheck with required fields."""
        _, client, _ = app_and_client
        payload = {"client_name": "test_client"}
        response = client.post("/api/status", json=payload)
        json_data = response.json()
        
        # Should have id, client_name, timestamp
        assert "id" in json_data
        assert "client_name" in json_data
        assert "timestamp" in json_data
        assert json_data["client_name"] == "test_client"
    
    def test_post_status_generates_uuid(self, app_and_client):
        """Verify POST /api/status generates a unique id (UUID)."""
        _, client, _ = app_and_client
        payload = {"client_name": "test_client"}
        response = client.post("/api/status", json=payload)
        json_data = response.json()
        
        # id should be a non-empty string (UUID format)
        assert isinstance(json_data["id"], str)
        assert len(json_data["id"]) > 0
    
    def test_post_status_generates_timestamp(self, app_and_client):
        """Verify POST /api/status generates a timestamp."""
        _, client, _ = app_and_client
        payload = {"client_name": "test_client"}
        response = client.post("/api/status", json=payload)
        json_data = response.json()
        
        # timestamp should be ISO format datetime string
        assert isinstance(json_data["timestamp"], str)
        # Should be parseable as ISO datetime
        datetime.fromisoformat(json_data["timestamp"])
    
    def test_post_status_calls_mongodb_insert(self, app_and_client):
        """Verify POST /api/status calls MongoDB insert_one."""
        _, client, mock_deps = app_and_client
        mock_client, mock_db, mock_collection = mock_deps
        
        payload = {"client_name": "test_client"}
        response = client.post("/api/status", json=payload)
        
        assert response.status_code == 200
        # insert_one should be called at least once
        assert mock_collection.insert_one.called
    
    def test_post_status_requires_client_name(self, app_and_client):
        """Verify POST /api/status requires client_name field."""
        _, client, _ = app_and_client
        payload = {}  # Missing client_name
        response = client.post("/api/status", json=payload)
        
        # Should return 422 Unprocessable Entity (validation error)
        assert response.status_code == 422


# ============================================================================
# P0.4: GET /api/status (Retrieve Status Checks)
# ============================================================================

class TestStatusGetEndpoint:
    """Test GET /api/status endpoint."""
    
    def test_get_status_returns_200(self, app_and_client):
        """Verify GET /api/status returns status 200."""
        _, client, mock_deps = app_and_client
        mock_client, mock_db, mock_collection = mock_deps
        
        # Setup mock to return empty list
        mock_collection.find.return_value.to_list = mock.AsyncMock(return_value=[])
        
        response = client.get("/api/status")
        assert response.status_code == 200
    
    def test_get_status_returns_list(self, app_and_client):
        """Verify GET /api/status returns a list."""
        _, client, mock_deps = app_and_client
        mock_client, mock_db, mock_collection = mock_deps
        
        # Setup mock to return empty list
        mock_collection.find.return_value.to_list = mock.AsyncMock(return_value=[])
        
        response = client.get("/api/status")
        json_data = response.json()
        
        assert isinstance(json_data, list)
    
    def test_get_status_calls_mongodb_find(self, app_and_client):
        """Verify GET /api/status calls MongoDB find."""
        _, client, mock_deps = app_and_client
        mock_client, mock_db, mock_collection = mock_deps
        
        # Setup mock
        mock_collection.find.return_value.to_list = mock.AsyncMock(return_value=[])
        
        response = client.get("/api/status")
        
        assert response.status_code == 200
        # find should be called
        assert mock_collection.find.called
    
    def test_get_status_excludes_mongodb_id(self, app_and_client):
        """Verify GET /api/status calls find with _id exclusion."""
        _, client, mock_deps = app_and_client
        mock_client, mock_db, mock_collection = mock_deps
        
        # Setup mock
        mock_collection.find.return_value.to_list = mock.AsyncMock(return_value=[])
        
        response = client.get("/api/status")
        
        assert response.status_code == 200
        # find should be called with exclusion of _id field
        mock_collection.find.assert_called_with({}, {"_id": 0})
    
    def test_get_status_returns_stored_records(self, app_and_client):
        """Verify GET /api/status returns stored status check records."""
        _, client, mock_deps = app_and_client
        mock_client, mock_db, mock_collection = mock_deps
        
        # Mock stored records
        stored_records = [
            {
                "id": "test-uuid-1",
                "client_name": "client_1",
                "timestamp": "2024-01-01T12:00:00+00:00"
            }
        ]
        mock_collection.find.return_value.to_list = mock.AsyncMock(return_value=stored_records)
        
        response = client.get("/api/status")
        json_data = response.json()
        
        assert len(json_data) == 1
        assert json_data[0]["client_name"] == "client_1"
    
    def test_get_status_deserializes_timestamps(self, app_and_client):
        """Verify GET /api/status deserializes ISO timestamps to datetime."""
        _, client, mock_deps = app_and_client
        mock_client, mock_db, mock_collection = mock_deps
        
        # Mock stored records with ISO timestamp string
        stored_records = [
            {
                "id": "test-uuid-1",
                "client_name": "client_1",
                "timestamp": "2024-01-01T12:00:00+00:00"
            }
        ]
        mock_collection.find.return_value.to_list = mock.AsyncMock(return_value=stored_records)
        
        response = client.get("/api/status")
        json_data = response.json()
        
        # Should still be a string in JSON, but must be parseable
        assert isinstance(json_data[0]["timestamp"], str)
        # Verify it's a valid datetime string
        datetime.fromisoformat(json_data[0]["timestamp"])


# ============================================================================
# P0.5: Pydantic Schema Validation
# ============================================================================

class TestPydanticSchemas:
    """Test Pydantic model validation for StatusCheck and StatusCheckCreate."""
    
    def test_status_check_create_requires_client_name(self):
        """Verify StatusCheckCreate requires client_name."""
        from backend.server import StatusCheckCreate
        
        with pytest.raises(ValidationError):
            StatusCheckCreate()  # Missing required field
    
    def test_status_check_create_accepts_client_name(self):
        """Verify StatusCheckCreate accepts client_name."""
        from backend.server import StatusCheckCreate
        
        model = StatusCheckCreate(client_name="test_client")
        assert model.client_name == "test_client"
    
    def test_status_check_generates_default_id(self):
        """Verify StatusCheck generates default id (UUID)."""
        from backend.server import StatusCheck
        
        model = StatusCheck(client_name="test_client")
        assert model.id is not None
        assert isinstance(model.id, str)
        assert len(model.id) > 0
    
    def test_status_check_generates_default_timestamp(self):
        """Verify StatusCheck generates default timestamp."""
        from backend.server import StatusCheck
        
        before = datetime.now(timezone.utc)
        model = StatusCheck(client_name="test_client")
        after = datetime.now(timezone.utc)
        
        assert model.timestamp is not None
        assert isinstance(model.timestamp, datetime)
        assert before <= model.timestamp <= after
    
    def test_status_check_accepts_explicit_id(self):
        """Verify StatusCheck accepts explicit id."""
        from backend.server import StatusCheck
        
        test_id = "explicit-id"
        model = StatusCheck(id=test_id, client_name="test_client")
        assert model.id == test_id
    
    def test_status_check_accepts_explicit_timestamp(self):
        """Verify StatusCheck accepts explicit timestamp."""
        from backend.server import StatusCheck
        
        test_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        model = StatusCheck(client_name="test_client", timestamp=test_time)
        assert model.timestamp == test_time
    
    def test_status_check_ignores_extra_fields(self):
        """Verify StatusCheck ignores extra fields (MongoDB _id)."""
        from backend.server import StatusCheck
        
        # Should not raise validation error when extra fields present
        model = StatusCheck(
            client_name="test_client",
            _id="mongodb_id"  # Extra field, should be ignored
        )
        assert model.client_name == "test_client"
        # _id should not be in model attributes
        assert not hasattr(model, "_id") or model._id is None
    
    def test_status_check_model_dump_includes_required_fields(self):
        """Verify StatusCheck.model_dump() includes required fields."""
        from backend.server import StatusCheck
        
        model = StatusCheck(client_name="test_client")
        dump = model.model_dump()
        
        assert "id" in dump
        assert "client_name" in dump
        assert "timestamp" in dump
        assert dump["client_name"] == "test_client"


# ============================================================================
# P0.6: Integration - Full POST/GET Cycle
# ============================================================================

class TestStatusCheckFullCycle:
    """Test full POST + GET cycle for status checks."""
    
    def test_post_then_get_status_checks(self, app_and_client):
        """Verify full cycle: POST status check, then GET all status checks."""
        _, client, mock_deps = app_and_client
        mock_client, mock_db, mock_collection = mock_deps
        
        # Step 1: POST a status check
        post_payload = {"client_name": "test_cycle"}
        post_response = client.post("/api/status", json=post_payload)
        assert post_response.status_code == 200
        post_data = post_response.json()
        
        # Step 2: Setup mock to return the created record on GET
        mock_collection.find.return_value.to_list = mock.AsyncMock(
            return_value=[
                {
                    "id": post_data["id"],
                    "client_name": post_data["client_name"],
                    "timestamp": post_data["timestamp"]
                }
            ]
        )
        
        # Step 3: GET status checks
        get_response = client.get("/api/status")
        assert get_response.status_code == 200
        get_data = get_response.json()
        
        # Verify record is in the list
        assert len(get_data) == 1
        assert get_data[0]["client_name"] == "test_cycle"
        assert get_data[0]["id"] == post_data["id"]
