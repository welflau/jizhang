import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, DATABASE_PATH
import os
import aiosqlite


@pytest.fixture(scope="function")
async def test_db():
    """Create a test database for each test."""
    test_db_path = "test_app.db"
    os.environ["DATABASE_PATH"] = test_db_path
    
    # Initialize test database
    await init_db()
    
    yield test_db_path
    
    # Cleanup
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def client(test_db):
    """Create test client."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_register_success_with_email(test_db):
    """Test successful user registration with email."""
    client = TestClient(app)
    
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "SecurePass123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_register_success_with_phone(test_db):
    """Test successful user registration with phone number."""
    client = TestClient(app)
    
    response = client.post(
        "/api/auth/register",
        json={
            "phone": "13800138000",
            "password": "SecurePass123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["phone"] == "13800138000"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(test_db):
    """Test registration with duplicate email fails."""
    client = TestClient(app)
    
    # First registration
    client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "SecurePass123"
        }
    )
    
    # Second registration with same email
    response = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "AnotherPass456"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_weak_password(test_db):
    """Test registration with weak password fails."""
    client = TestClient(app)
    
    # Password without digits
    response = client.post(
        "/api/auth/register",
        json={
            "email": "weak@example.com",
            "password": "WeakPassword"
        }
    )
    
    assert response.status_code == 422
    
    # Password without letters
    response = client.post(
        "/api/auth/register",
        json={
            "email": "weak2@example.com",
            "password": "12345678"
        }
    )
    
    assert response.status_code == 422
    
    # Password too short
    response = client.post(
        "/api/auth/register",
        json={
            "email": "weak3@example.com",
            "password": "Pass1"
        }
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_phone(test_db):
    """Test registration with invalid phone number fails."""
    client = TestClient(app)
    
    response = client.post(
        "/api/auth/register",
        json={
            "phone": "12345",
            "password": "SecurePass123"
        }
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_identifier(test_db):
    """Test registration without email or phone fails."""
    client = TestClient(app)
    
    response = client.post(
        "/api/auth/register",
        json={
            "password": "SecurePass123"
        }
    )
    
    assert response.status_code == 422
