import pytest
from httpx import AsyncClient
from backend.app.main import app
from backend.app.core.database import engine, Base
import os

TEST_DB = "test_app.db"


@pytest.fixture(scope="function")
async def test_db():
    """Create test database."""
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///./{TEST_DB}"
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.mark.asyncio
async def test_login_success(test_db):
    """Test successful login."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user first
        await client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "securepass123"}
        )
        
        # Login
        response = await client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "securepass123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(test_db):
    """Test login with incorrect password."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        await client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "correctpass123"}
        )
        
        # Login with wrong password
        response = await client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "wrongpass123"}
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(test_db):
    """Test login with non-existent email."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "anypass123"}
        )
        
        assert response.status_code == 401