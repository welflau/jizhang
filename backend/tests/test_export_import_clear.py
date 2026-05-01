import pytest
import json
import os
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, init_db, DB_PATH
import aiosqlite
from datetime import datetime

# Use test database
test_db_path = "./data/test_app.db"
os.environ["DB_PATH"] = test_db_path
os.environ["ADMIN_TOKEN"] = "test_admin_token_12345"

client = TestClient(app)

@pytest.fixture(autouse=True)
async def setup_teardown():
    """Setup test database before each test and cleanup after"""
    # Remove existing test db
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Initialize fresh database
    await init_db()
    
    # Insert test data
    async with aiosqlite.connect(test_db_path) as db:
        await db.execute("""
            INSERT INTO access_logs (id, timestamp, ip, user_agent, path)
            VALUES (1, '2024-01-01T10:00:00', '192.168.1.1', 'Mozilla/5.0', '/home')
        """)
        await db.execute("""
            INSERT INTO access_logs (id, timestamp, ip, user_agent, path)
            VALUES (2, '2024-01-01T11:00:00', '192.168.1.2', 'Chrome/120', '/about')
        """)
        await db.commit()
    
    yield
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_export_records():
    """Test export endpoint returns all records sorted by timestamp"""
    response = client.get("/api/export")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    
    # Check sorting (descending by timestamp)
    assert data[0]["id"] == 2
    assert data[1]["id"] == 1
    
    # Verify fields
    assert "timestamp" in data[0]
    assert "ip" in data[0]
    assert data[0]["ip"] == "192.168.1.2"

def test_import_valid_records():
    """Test import endpoint with valid JSON data"""
    import_data = [
        {
            "id": 100,
            "timestamp": "2024-01-02T12:00:00",
            "ip": "10.0.0.1",
            "user_agent": "TestAgent",
            "path": "/test"
        },
        {
            "id": 101,
            "timestamp": "2024-01-02T13:00:00",
            "ip": "10.0.0.2",
            "user_agent": None,
            "path": None
        }
    ]
    
    files = {"file": ("test.json", json.dumps(import_data), "application/json")}
    response = client.post("/api/import", files=files)
    
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["imported_count"] == 2
    assert result["skipped_count"] == 0

def test_import_duplicate_ids():
    """Test import skips records with duplicate IDs"""
    import_data = [
        {
            "id": 1,  # Already exists
            "timestamp": "2024-01-02T12:00:00",
            "ip": "10.0.0.1",
            "user_agent": "TestAgent",
            "path": "/test"
        }
    ]
    
    files = {"file": ("test.json", json.dumps(import_data), "application/json")}
    response = client.post("/api/import", files=files)
    
    assert response.status_code == 200
    result = response.json()
    assert result["imported_count"] == 0
    assert result["skipped_count"] == 1
    assert len(result["errors"]) > 0

def test_import_invalid_json():
    """Test import rejects invalid JSON format"""
    files = {"file": ("test.json", "not valid json", "application/json")}
    response = client.post("/api/import", files=files)
    
    assert response.status_code == 400
    assert "Invalid JSON format" in response.json()["detail"]

def test_clear_with_valid_token():
    """Test clear endpoint with valid admin token"""
    headers = {"Authorization": "Bearer test_admin_token_12345"}
    response = client.post("/api/clear", headers=headers)
    
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["deleted"] == 2
    
    # Verify records are deleted
    export_response = client.get("/api/export")
    assert len(export_response.json()) == 0

def test_clear_without_token():
    """Test clear endpoint rejects request without token"""
    response = client.post("/api/clear")
    
    assert response.status_code == 401
    assert "Authorization header required" in response.json()["detail"]

def test_clear_with_invalid_token():
    """Test clear endpoint rejects invalid token"""
    headers = {"Authorization": "Bearer wrong_token"}
    response = client.post("/api/clear", headers=headers)
    
    assert response.status_code == 401
    assert "Invalid or missing admin token" in response.json()["detail"]

def test_clear_invalid_auth_format():
    """Test clear endpoint rejects malformed authorization header"""
    headers = {"Authorization": "InvalidFormat token123"}
    response = client.post("/api/clear", headers=headers)
    
    assert response.status_code == 401
    assert "Invalid authorization format" in response.json()["detail"]
