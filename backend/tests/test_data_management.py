import pytest
import json
from fastapi.testclient import TestClient
from datetime import datetime
from io import BytesIO

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import AccessLog

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and clean up after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a database session for tests"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_records(db_session):
    """Create sample records for testing"""
    records = [
        AccessLog(
            id=1,
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            ip="192.168.1.1",
            user_agent="Mozilla/5.0"
        ),
        AccessLog(
            id=2,
            timestamp=datetime(2024, 1, 2, 11, 0, 0),
            ip="192.168.1.2",
            user_agent="Chrome/120.0"
        ),
        AccessLog(
            id=3,
            timestamp=datetime(2024, 1, 3, 12, 0, 0),
            ip="192.168.1.3",
            user_agent="Safari/17.0"
        )
    ]
    for record in records:
        db_session.add(record)
    db_session.commit()
    return records


class TestExportAPI:
    def test_export_empty_database(self):
        """Test export with no records"""
        response = client.get("/api/export")
        assert response.status_code == 200
        assert response.json() == []
        assert "attachment" in response.headers.get("content-disposition", "")
    
    def test_export_with_records(self, sample_records):
        """Test export with existing records"""
        response = client.get("/api/export")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        
        # Verify sorting (newest first)
        assert data[0]["id"] == 3
        assert data[1]["id"] == 2
        assert data[2]["id"] == 1
        
        # Verify fields
        assert "timestamp" in data[0]
        assert "ip" in data[0]
        assert "user_agent" in data[0]
    
    def test_export_response_headers(self, sample_records):
        """Test export response has correct headers"""
        response = client.get("/api/export")
        assert "content-disposition" in response.headers
        assert "access_logs_export.json" in response.headers["content-disposition"]


class TestImportAPI:
    def test_import_valid_json(self):
        """Test import with valid JSON data"""
        data = [
            {
                "id": 100,
                "timestamp": "2024-01-01T10:00:00",
                "ip": "10.0.0.1",
                "user_agent": "TestAgent/1.0"
            },
            {
                "id": 101,
                "timestamp": "2024-01-02T11:00:00",
                "ip": "10.0.0.2",
                "user_agent": "TestAgent/2.0"
            }
        ]
        
        json_content = json.dumps(data).encode()
        files = {"file": ("test.json", BytesIO(json_content), "application/json")}
        
        response = client.post("/api/import", files=files)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["imported_count"] == 2
        assert result["skipped_count"] == 0
    
    def test_import_invalid_json(self):
        """Test import with invalid JSON"""
        files = {"file": ("test.json", BytesIO(b"not valid json"), "application/json")}
        
        response = client.post("/api/import", files=files)
        assert response.status_code == 400
        assert "Invalid JSON format" in response.json()["detail"]
    
    def test_import_duplicate_ids(self, sample_records):
        """Test import with duplicate IDs"""
        data = [
            {
                "id": 1,  # Duplicate
                "timestamp": "2024-01-01T10:00:00",
                "ip": "10.0.0.1",
                "user_agent": "TestAgent/1.0"
            },
            {
                "id": 200,  # New
                "timestamp": "2024-01-02T11:00:00",
                "ip": "10.0.0.2",
                "user_agent": "TestAgent/2.0"
            }
        ]
        
        json_content = json.dumps(data).encode()
        files = {"file": ("test.json", BytesIO(json_content), "application/json")}
        
        response = client.post("/api/import", files=files)
        assert response.status_code == 200
        
        result = response.json()
        assert result["imported_count"] == 1
        assert result["skipped_count"] == 1
    
    def test_import_not_array(self):
        """Test import with non-array JSON"""
        data = {"not": "an array"}
        json_content = json.dumps(data).encode()
        files = {"file": ("test.json", BytesIO(json_content), "application/json")}
        
        response = client.post("/api/import", files=files)
        assert response.status_code == 400
        assert "must be an array" in response.json()["detail"]


class TestClearAPI:
    def test_clear_without_token(self):
        """Test clear without authorization token"""
        response = client.post("/api/clear")
        assert response.status_code == 401
        assert "authorization token required" in response.json()["detail"].lower()
    
    def test_clear_with_short_token(self):
        """Test clear with token too short"""
        response = client.post("/api/clear?token=short")
        assert response.status_code == 401
    
    def test_clear_with_valid_token(self, sample_records):
        """Test clear with valid token"""
        headers = {"Authorization": "Bearer validtoken12345"}
        response = client.post("/api/clear", headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["deleted_count"] == 3
        
        # Verify database is empty
        verify_response = client.get("/api/export")
        assert len(verify_response.json()) == 0
    
    def test_clear_with_query_token(self, sample_records):
        """Test clear with token in query parameter"""
        response = client.post("/api/clear?token=validtoken12345")
        
        assert response.status_code == 200
        result = response.json()
        assert result["deleted_count"] == 3
    
    def test_clear_empty_database(self):
        """Test clear on empty database"""
        headers = {"Authorization": "Bearer validtoken12345"}
        response = client.post("/api/clear", headers=headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["deleted_count"] == 0


class TestIntegration:
    def test_export_import_cycle(self, sample_records):
        """Test full export-import cycle"""
        # Export
        export_response = client.get("/api/export")
        exported_data = export_response.json()
        assert len(exported_data) == 3
        
        # Clear
        clear_response = client.post(
            "/api/clear",
            headers={"Authorization": "Bearer validtoken12345"}
        )
        assert clear_response.json()["deleted_count"] == 3
        
        # Import back
        json_content = json.dumps(exported_data).encode()
        files = {"file": ("export.json", BytesIO(json_content), "application/json")}
        import_response = client.post("/api/import", files=files)
        
        assert import_response.status_code == 200
        result = import_response.json()
        assert result["imported_count"] == 3
        
        # Verify data restored
        final_export = client.get("/api/export")
        assert len(final_export.json()) == 3
