import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.models.user import User
from backend.services.user_service import UserService
from backend.schemas.user import UpdateUserInfoRequest
from backend.database import Base
from fastapi import HTTPException
import bcrypt

# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def db_session():
    """Create test database session"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    AsyncTestSession = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with AsyncTestSession() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
async def test_user(db_session):
    """Create test user"""
    password = "Test123456"
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=password_hash,
        nickname="Test User",
        avatar_url="https://example.com/avatar.jpg",
        preferences='{"theme": "dark", "language": "en"}'
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.mark.asyncio
async def test_update_nickname(db_session, test_user):
    """Test nickname update"""
    new_nickname = "Updated Nickname"
    await UserService.update_nickname(db_session, test_user, new_nickname)
    await db_session.commit()
    await db_session.refresh(test_user)
    
    assert test_user.nickname == new_nickname

@pytest.mark.asyncio
async def test_update_avatar(db_session, test_user):
    """Test avatar URL update"""
    new_avatar = "https://example.com/new-avatar.jpg"
    await UserService.update_avatar(db_session, test_user, new_avatar)
    await db_session.commit()
    await db_session.refresh(test_user)
    
    assert test_user.avatar_url == new_avatar

@pytest.mark.asyncio
async def test_update_password_success(db_session, test_user):
    """Test successful password update"""
    current_password = "Test123456"
    new_password = "NewPass789"
    
    await UserService.update_password(
        db_session,
        test_user,
        current_password,
        new_password
    )
    await db_session.commit()
    await db_session.refresh(test_user)
    
    # Verify new password works
    assert bcrypt.checkpw(
        new_password.encode("utf-8"),
        test_user.password_hash.encode("utf-8")
    )

@pytest.mark.asyncio
async def test_update_password_wrong_current(db_session, test_user):
    """Test password update with wrong current password"""
    with pytest.raises(HTTPException) as exc_info:
        await UserService.update_password(
            db_session,
            test_user,
            "WrongPassword123",
            "NewPass789"
        )
    
    assert exc_info.value.status_code == 400
    assert "incorrect" in exc_info.value.detail.lower()

@pytest.mark.asyncio
async def test_update_preferences(db_session, test_user):
    """Test preferences update and merge"""
    new_prefs = {"notifications": True, "theme": "light"}
    await UserService.update_preferences(db_session, test_user, new_prefs)
    await db_session.commit()
    await db_session.refresh(test_user)
    
    prefs = test_user.get_preferences()
    assert prefs["notifications"] is True
    assert prefs["theme"] == "light"
    assert prefs["language"] == "en"  # Original value preserved

@pytest.mark.asyncio
async def test_update_user_info_all_fields(db_session, test_user):
    """Test updating all fields at once"""
    update_data = UpdateUserInfoRequest(
        nickname="New Nickname",
        avatar_url="https://example.com/new.jpg",
        current_password="Test123456",
        new_password="NewPass789",
        preferences={"theme": "auto"}
    )
    
    updated_user = await UserService.update_user_info(
        db_session,
        test_user.id,
        update_data
    )
    
    assert updated_user.nickname == "New Nickname"
    assert updated_user.avatar_url == "https://example.com/new.jpg"
    assert updated_user.get_preferences()["theme"] == "auto"
    assert bcrypt.checkpw(
        "NewPass789".encode("utf-8"),
        updated_user.password_hash.encode("utf-8")
    )

@pytest.mark.asyncio
async def test_update_user_info_partial(db_session, test_user):
    """Test updating only some fields"""
    original_nickname = test_user.nickname
    original_avatar = test_user.avatar_url
    
    update_data = UpdateUserInfoRequest(
        preferences={"new_setting": "value"}
    )
    
    updated_user = await UserService.update_user_info(
        db_session,
        test_user.id,
        update_data
    )
    
    # Unchanged fields preserved
    assert updated_user.nickname == original_nickname
    assert updated_user.avatar_url == original_avatar
    # New preference added
    assert updated_user.get_preferences()["new_setting"] == "value"

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(db_session):
    """Test getting non-existent user"""
    with pytest.raises(HTTPException) as exc_info:
        await UserService.get_user_by_id(db_session, 99999)
    
    assert exc_info.value.status_code == 404