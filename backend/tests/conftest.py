import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash

# 测试数据库配置
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db: Session) -> User:
    """创建测试用户"""
    user = User(
        email="test@example.com",
        phone="13800138000",
        hashed_password=get_password_hash("Test123456!"),
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def verified_user(db: Session) -> User:
    """创建已验证的测试用户"""
    user = User(
        email="verified@example.com",
        phone="13900139000",
        hashed_password=get_password_hash("Test123456!"),
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(client: TestClient, verified_user: User) -> dict:
    """获取认证头部"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": verified_user.email,
            "password": "Test123456!"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def multiple_users(db: Session) -> list[User]:
    """创建多个测试用户"""
    users = []
    for i in range(3):
        user = User(
            email=f"user{i}@example.com",
            phone=f"1380013800{i}",
            hashed_password=get_password_hash("Test123456!"),
            is_active=True,
            is_verified=True
        )
        db.add(user)
        users.append(user)
    db.commit()
    for user in users:
        db.refresh(user)
    return users


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def reset_settings():
    """重置配置为测试环境"""
    original_values = {}
    
    # 保存原始值
    original_values["ACCESS_TOKEN_EXPIRE_MINUTES"] = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    original_values["REFRESH_TOKEN_EXPIRE_DAYS"] = settings.REFRESH_TOKEN_EXPIRE_DAYS
    
    # 设置测试值
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    settings.REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    yield
    
    # 恢复原始值
    for key, value in original_values.items():
        setattr(settings, key, value)


# 测试数据常量
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PHONE = "13800138000"
TEST_USER_PASSWORD = "Test123456!"
TEST_USER_NEW_PASSWORD = "NewTest123456!"
