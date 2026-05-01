import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.middleware.auth import AuthMiddleware
import aiosqlite
import bcrypt
import json
import os

client = TestClient(app)

# Test database path
TEST_DB = "test_app.db"

@pytest.fixture(scope="module")
async def setup_test_db():
    """Setup test database with sample user"""
    # Remove existing test db
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    async with aiosqlite.connect(TEST_DB) as db:
        # Create users table
        await db.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nickname TEXT,
                avatar TEXT,
                preferences TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Insert test user
        password_hash = bcrypt.hashpw(b"TestPass123", bcrypt.gensalt()).decode('utf-8')
        await db.execute(
            "INSERT INTO users (username, email, password_hash, nickname, avatar, preferences, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))",
            ("testuser", "test@example.com", password_hash, "TestNick", "https://example.com/avatar.jpg", json.dumps({"theme": "light"}))
        )
        await db.commit()
    
    yield
    
    # Cleanup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def get_test_token():
    """Generate test JWT token"""
    return AuthMiddleware.create_token(user_id=1, username="testuser")

@pytest.mark.asyncio
async def test_get_profile_success(setup_test_db):
    """Test GET /api/user/profile with valid token"""
    # Override db path for testing
    from backend.routes import user_routes
    user_routes.user_service.db_path = TEST_DB
    
    token = get_test_token()
    response = client.get(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["nickname"] == "TestNick"
    assert "password_hash" not in data  # Should not expose password

@pytest.mark.asyncio
async def test_get_profile_unauthorized():
    """Test GET /api/user/profile without token"""
    response = client.get("/api/user/profile")
    assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing auth

@pytest.mark.asyncio
async def test_get_profile_invalid_token():
    """Test GET /api/user/profile with invalid token"""
    response = client.get(
        "/api/user/profile",
        headers={"Authorization": "Bearer invalid_token_xyz"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_profile_nickname_success(setup_test_db):
    """Test PATCH /api/user/profile - update nickname"""
    from backend.routes import user_routes
    user_routes.user_service.db_path = TEST_DB
    
    token = get_test_token()
    response = client.patch(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"nickname": "NewNickname"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == "NewNickname"

@pytest.mark.asyncio
async def test_update_profile_avatar_success(setup_test_db):
    """Test PATCH /api/user/profile - update avatar"""
    from backend.routes import user_routes
    user_routes.user_service.db_path = TEST_DB
    
    token = get_test_token()
    response = client.patch(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"avatar": "https://newavatar.com/image.png"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["avatar"] == "https://newavatar.com/image.png"

@pytest.mark.asyncio
async def test_update_profile_invalid_avatar():
    """Test PATCH /api/user/profile - invalid avatar URL"""
    from backend.routes import user_routes
    user_routes.user_service.db_path = TEST_DB
    
    token = get_test_token()
    response = client.patch(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"avatar": "not-a-valid-url"}
    )
    
    assert response.status_code == 422  # Pydantic validation error

@pytest.mark.asyncio
async def test_update_profile_password_success(setup_test_db):
    """Test PATCH /api/user/profile - change password"""
    from backend.routes import user_routes
    user_routes.user_service.db_path = TEST_DB
    
    token = get_test_token()
    response = client.patch(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "TestPass123",
            "new_password": "NewPass456"
        }
    )
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_profile_password_wrong_current():
    """Test PATCH /api/user/profile - wrong current password"""
    from backend.routes import user_routes
    user_routes.user_service.db_path = TEST_DB
    
    token = get_test_token()
    response = client.patch(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "WrongPassword",
            "new_password": "NewPass456"
        }
    )
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_update_profile_password_missing_current():
    """Test PATCH /api/user/profile - new password without current"""
    from backend.routes import user_routes
    user_routes.user_service.db_path = TEST_DB
    
    token = get_test_token()
    response = client.patch(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"new_password": "NewPass456"}
    )
    
    assert response.status_code == 400
    assert "current_password" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_update_profile_weak_password():
    """Test PATCH /api/user/profile - weak password validation"""
    from backend.routes import user_routes
    user_routes.user_service.db_path = TEST_DB
    
    token = get_test_token()
    response = client.patch(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "TestPass123",
            "new_password": "weak"  # Too short, no uppercase/digit
        }
    )
    
    assert response.status_code == 422  # Pydantic validation error

@pytest.mark.asyncio
async def test_update_profile_preferences_success(setup_test_db):
    """Test PATCH /api/user/profile - update preferences"""
    from backend.routes import user_routes
    user_routes.user_service.db_path = TEST_DB
    
    token = get_test_token()
    response = client.patch(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "preferences": {
                "theme": "dark",
                "language": "zh",
                "notifications_enabled": False
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["preferences"]["theme"] == "dark"
    assert data["preferences"]["language"] == "zh"
    assert data["preferences"]["notifications_enabled"] is False

@pytest.mark.asyncio
async def test_update_profile_multiple_fields(setup_test_db):
    """Test PATCH /api/user/profile - update multiple fields at once"""
    from backend.routes import user_routes
    user_routes.user_service.db_path = TEST_DB
    
    token = get_test_token()
    response = client.patch(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nickname": "MultiUpdate",
            "avatar": "https://multi.com/avatar.jpg",
            "preferences": {"theme": "dark"}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nickname"] == "MultiUpdate"
    assert data["avatar"] == "https://multi.com/avatar.jpg"
    assert data["preferences"]["theme"] == "dark"