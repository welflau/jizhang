import pytest
from httpx import AsyncClient
from backend.app.main import app
from backend.app.core.database import init_db, engine, Base
import os

# Use test database
TEST_DB = "test_app.db"


@pytest.fixture(scope="function")
async def test_db():
    """Create test database for each test."""
    # Override database URL for testing
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///./{TEST_DB}"
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.mark.asyncio
async def test_register_success(test_db):
    """Test successful user registration."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "securepass123"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password


@pytest.mark.asyncio
async def test_register_duplicate_email(test_db):
    """Test registration with existing email."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First registration
        await client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "pass123456"}
        )
        
        # Duplicate registration
        response = await client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "different123"}
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email(test_db):
    """Test registration with invalid email format."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={"email": "not-an-email", "password": "pass123456"}
        )
        
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_short_password(test_db):
    """Test registration with password too short."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "short"}
        )
        
        assert response.status_code == 422  # Validation error