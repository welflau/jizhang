import pytest
import aiosqlite
import os
import json
from datetime import datetime

from services.user_service import UserService
from fastapi import HTTPException

# Test database path
TEST_DB = "test_app.db"

@pytest.fixture
async def db_setup():
    """Setup test database"""
    # Remove existing test db
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    # Create schema
    async with aiosqlite.connect(TEST_DB) as db:
        await db.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nickname TEXT,
                avatar TEXT,
                email TEXT,
                preferences TEXT DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        # Insert test user with bcrypt hashed password for "password123"
        import bcrypt
        password_hash = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode('utf-8')
        
        await db.execute("""
            INSERT INTO users (username, password_hash, nickname, email, preferences)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "testuser",
            password_hash,
            "Test User",
            "test@example.com",
            json.dumps({"theme": "light", "language": "en-US"})
        ))
        await db.commit()
    
    yield
    
    # Cleanup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

@pytest.mark.asyncio
async def test_get_user_by_id(db_setup):
    """Test retrieving user by ID"""
    service = UserService(TEST_DB)
    user = await service.get_user_by_id(1)
    
    assert user is not None
    assert user['username'] == "testuser"
    assert user['nickname'] == "Test User"
    assert user['email'] == "test@example.com"
    assert isinstance(user['preferences'], dict)
    assert user['preferences']['theme'] == "light"

@pytest.mark.asyncio
async def test_get_user_not_found(db_setup):
    """Test retrieving non-existent user"""
    service = UserService(TEST_DB)
    user = await service.get_user_by_id(999)
    
    assert user is None

@pytest.mark.asyncio
async def test_verify_password_correct(db_setup):
    """Test password verification with correct password"""
    service = UserService(TEST_DB)
    result = await service.verify_password(1, "password123")
    
    assert result is True

@pytest.mark.asyncio
async def test_verify_password_incorrect(db_setup):
    """Test password verification with incorrect password"""
    service = UserService(TEST_DB)
    result = await service.verify_password(1, "wrongpassword")
    
    assert result is False

@pytest.mark.asyncio
async def test_update_nickname(db_setup):
    """Test updating user nickname"""
    service = UserService(TEST_DB)
    updated = await service.update_user_info(
        user_id=1,
        nickname="New Nickname"
    )
    
    assert updated['nickname'] == "New Nickname"
    assert updated['username'] == "testuser"  # Other fields unchanged

@pytest.mark.asyncio
async def test_update_avatar(db_setup):
    """Test updating user avatar"""
    service = UserService(TEST_DB)
    avatar_url = "https://example.com/avatar.jpg"
    updated = await service.update_user_info(
        user_id=1,
        avatar=avatar_url
    )
    
    assert updated['avatar'] == avatar_url

@pytest.mark.asyncio
async def test_update_password_success(db_setup):
    """Test successful password update"""
    service = UserService(TEST_DB)
    
    # Update password
    await service.update_user_info(
        user_id=1,
        old_password="password123",
        new_password="newpass456"
    )
    
    # Verify new password works
    assert await service.verify_password(1, "newpass456") is True
    # Verify old password no longer works
    assert await service.verify_password(1, "password123") is False

@pytest.mark.asyncio
async def test_update_password_wrong_old_password(db_setup):
    """Test password update with incorrect old password"""
    service = UserService(TEST_DB)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.update_user_info(
            user_id=1,
            old_password="wrongpassword",
            new_password="newpass456"
        )
    
    assert exc_info.value.status_code == 401
    assert "incorrect" in exc_info.value.detail.lower()

@pytest.mark.asyncio
async def test_update_preferences(db_setup):
    """Test updating user preferences"""
    service = UserService(TEST_DB)
    new_prefs = {
        "theme": "dark",
        "notifications_enabled": True
    }
    
    updated = await service.update_user_info(
        user_id=1,
        preferences=new_prefs
    )
    
    assert updated['preferences']['theme'] == "dark"
    assert updated['preferences']['notifications_enabled'] is True

@pytest.mark.asyncio
async def test_update_preferences_merge(db_setup):
    """Test merging preferences with existing ones"""
    service = UserService(TEST_DB)
    
    # Update only theme, should preserve language
    updated = await service.update_preferences(
        user_id=1,
        preferences={"theme": "dark"}
    )
    
    assert updated['preferences']['theme'] == "dark"
    assert updated['preferences']['language'] == "en-US"  # Preserved

@pytest.mark.asyncio
async def test_update_multiple_fields(db_setup):
    """Test updating multiple fields at once"""
    service = UserService(TEST_DB)
    
    updated = await service.update_user_info(
        user_id=1,
        nickname="Multi Update",
        avatar="https://example.com/new.jpg",
        preferences={"theme": "dark"}
    )
    
    assert updated['nickname'] == "Multi Update"
    assert updated['avatar'] == "https://example.com/new.jpg"
    assert updated['preferences']['theme'] == "dark"

@pytest.mark.asyncio
async def test_update_nonexistent_user(db_setup):
    """Test updating non-existent user"""
    service = UserService(TEST_DB)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.update_user_info(
            user_id=999,
            nickname="Should Fail"
        )
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()