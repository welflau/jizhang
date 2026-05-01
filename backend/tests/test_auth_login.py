import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db
import os


@pytest.fixture(scope="function")
async def test_db():
    """Create a test database for each test."""
    test_db_path = "test_login.db"
    os.environ["DATABASE_PATH"] = test_db_path
    
    await init_db()
    
    yield test_db_path
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture
def client_with_user(test_db):
    """Create test client and register a test user."""
    client = TestClient(app)
    
    # Register test user
    client.post(
        "/api/auth/register",
        json={
            "email": "login@example.com",
            "password": "TestPass123"
        }
    )
    
    return client


@pytest.mark.asyncio
async def test_login_success_with_email(test_db, client_with_user):
    """Test successful login with email."""
    response = client_with_user.post(
        "/api/auth/login",
        json={
            "identifier": "login@example.com",
            "password": "TestPass123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_wrong_password(test_db, client_with_user):
    """Test login with wrong password fails."""
    response = client_with_user.post(
        "/api/auth/login",
        json={
            "identifier": "login@example.com",
            "password": "WrongPass123"
        }
    )
    
    assert response.status_code == 401
    assert "invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(test_db, client_with_user):
    """Test login with non-existent user fails."""
    response = client_with_user.post(
        "/api/auth/login",
        json={
            "identifier": "nonexistent@example.com",
            "password": "TestPass123"
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(test_db, client_with_user):
    """Test logout endpoint."""
    response = client_with_user.post("/api/auth/logout")
    
    assert response.status_code == 200
    assert "logged out" in response.json()["message"]
