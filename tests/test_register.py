import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from jose import jwt
import re

from app.main import app
from app.core.config import settings
from app.core.security import verify_password, get_password_hash
from app.models.user import User
from app.db.session import get_db

client = TestClient(app)


class TestUserRegistration:
    """用户注册测试"""

    def test_register_with_email_success(self, db_session):
        """测试邮箱注册成功"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
                "username": "testuser"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "id" in data
        assert "password" not in data

    def test_register_with_phone_success(self, db_session):
        """测试手机号注册成功"""
        response = client.post(
            "/api/auth/register",
            json={
                "phone": "13800138000",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
                "username": "phoneuser"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["phone"] == "13800138000"
        assert data["username"] == "phoneuser"

    def test_register_duplicate_email(self, db_session, test_user):
        """测试重复邮箱注册"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
                "username": "newuser"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_duplicate_phone(self, db_session, test_user_with_phone):
        """测试重复手机号注册"""
        response = client.post(
            "/api/auth/register",
            json={
                "phone": test_user_with_phone.phone,
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
                "username": "newuser"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email_format(self, db_session):
        """测试无效邮箱格式"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
                "username": "testuser"
            }
        )
        assert response.status_code == 422

    def test_register_invalid_phone_format(self, db_session):
        """测试无效手机号格式"""
        response = client.post(
            "/api/auth/register",
            json={
                "phone": "12345",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
                "username": "testuser"
            }
        )
        assert response.status_code == 422

    def test_register_weak_password(self, db_session):
        """测试弱密码"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "123",
                "password_confirm": "123",
                "username": "testuser"
            }
        )
        assert response.status_code == 422
        assert "password" in response.json()["detail"].lower()

    def test_register_password_mismatch(self, db_session):
        """测试密码不匹配"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "StrongPass123!",
                "password_confirm": "DifferentPass123!",
                "username": "testuser"
            }
        )
        assert response.status_code == 422
        assert "match" in response.json()["detail"].lower()

    def test_register_missing_credentials(self, db_session):
        """测试缺少邮箱和手机号"""
        response = client.post(
            "/api/auth/register",
            json={
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
                "username": "testuser"
            }
        )
        assert response.status_code == 422

    def test_register_password_encryption(self, db_session):
        """测试密码加密存储"""
        password = "StrongPass123!"
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": password,
                "password_confirm": password,
                "username": "testuser"
            }
        )
        assert response.status_code == 201
        
        # 验证数据库中密码已加密
        user = db_session.query(User).filter(User.email == "test@example.com").first()
        assert user.hashed_password != password
        assert verify_password(password, user.hashed_password)


class TestUserLogin:
    """用户登录测试"""

    def test_login_with_email_success(self, db_session, test_user):
        """测试邮箱登录成功"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_user.email,
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_login_with_phone_success(self, db_session, test_user_with_phone):
        """测试手机号登录成功"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_user_with_phone.phone,
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_wrong_password(self, db_session, test_user):
        """测试错误密码"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_user.email,
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, db_session):
        """测试不存在的用户"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent@example.com",
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 401

    def test_login_remember_me(self, db_session, test_user):
        """测试记住登录状态"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_user.email,
                "password": "TestPass123!",
                "remember_me": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # 验证refresh token过期时间更长
        refresh_token = data["refresh_token"]
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        assert (exp - now).days >= 7

    def test_login_inactive_user(self, db_session, inactive_user):
        """测试未激活用户登录"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": inactive_user.email,
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()

    def test_login_rate_limiting(self, db_session, test_user):
        """测试登录频率限制"""
        # 多次失败登录
        for _ in range(6):
            client.post(
                "/api/auth/login",
                json={
                    "username": test_user.email,
                    "password": "WrongPassword"
                }
            )
        
        # 第7次应该被限制
        response = client.post(
            "/api/auth/login",
            json={
                "username": test_user.email,
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 429


class TestJWTAuthentication:
    """JWT认证测试"""

    def test_access_protected_route_with_valid_token(self, db_session, test_user, auth_headers):
        """测试使用有效token访问受保护路由"""
        response = client.get(
            "/api/users/me",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email

    def test_access_protected_route_without_token(self, db_session):
        """测试无token访问受保护路由"""
        response = client.get("/api/users/me")
        assert response.status_code == 401

    def test_access_protected_route_with_invalid_token(self, db_session):
        """测试使用无效token访问受保护路由"""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_access_protected_route_with_expired_token(self, db_session, expired_token):
        """测试使用过期token访问受保护路由"""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_refresh_token(self, db_session, test_user):
        """测试刷新token"""
        # 先登录获取refresh token
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": test_user.email,
                "password": "TestPass123!"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # 使用refresh token获取新的access token
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, db_session):
        """测试无效refresh token"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        assert response.status_code == 401

    def test_token_contains_user_info(self, db_session, test_user, auth_token):
        """测试token包含用户信息"""
        payload = jwt.decode(auth_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == str(test_user.id)
        assert payload["email"] == test_user.email
        assert "exp" in payload


class TestPasswordReset:
    """密码重置测试"""

    def test_request_password_reset(self, db_session, test_user):
        """测试请求密码重置"""
        response = client.post(
            "/api/auth/password-reset/request",
            json={"email": test_user.email}
        )
        assert response.status_code == 200
        assert "email sent" in response.json()["message"].lower()

    def test_request_password_reset_nonexistent_email(self, db_session):
        """测试不存在的邮箱请求密码重置"""
        response = client.post(
            "/api/auth/password-reset/request",
            json={"email": "nonexistent@example.com"}
        )
        # 为了安全，即使邮箱不存在也返回成功
        assert response.status_code == 200

    def test_verify_reset_token(self, db_session, test_user, password_reset_token):
        """测试验证重置token"""
        response = client.get(
            f"/api/auth/password-reset/verify/{password_reset_token}"
        )
        assert response.status_code == 200
        assert response.json()["valid"] is True

    def test_verify_invalid_reset_token(self, db_session):
        """测试验证无效重置token"""
        response = client.get(
            "/api/auth/password-reset/verify/invalid_token"
        )
        assert response.status_code == 400

    def test_reset_password(self, db_session, test_user, password_reset_token):
        """测试重置密码"""
        new_password = "NewStrongPass123!"
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": password_reset_token,
                "new_password": new_password,
                "new_password_confirm": new_password
            }
        )
        assert response.status_code == 200
        
        # 验证可以用新密码登录
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": test_user.email,
                "password": new_password
            }
        )
        assert login_response.status_code == 200

    def test_reset_password_token_expiry(self, db_session, expired_reset_token):
        """测试过期的重置token"""
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": expired_reset_token,
                "new_password": "NewPass123!",
                "new_password_confirm": "NewPass123!"
            }
        )
        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()

    def test_reset_password_mismatch(self, db_session, password_reset_token):
        """测试重置密码不匹配"""
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": password_reset_token,
                "new_password": "NewPass123!",
                "new_password_confirm": "DifferentPass123!"
            }
        )
        assert response.status_code == 422

    def test_reset_password_same_as_old(self, db_session, test_user, password_reset_token):
        """测试新密码与旧密码相同"""
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": password_reset_token,
                "new_password": "TestPass123!",
                "new_password_confirm": "TestPass123!"
            }
        )
        assert response.status_code == 400
        assert "same" in response.json()["detail"].lower()


class TestLogout:
    """登出测试"""

    def test_logout_success(self, db_session, test_user, auth_headers):
        """测试登出成功"""
        response = client.post(
            "/api/auth/logout",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()

    def test_logout_without_token(self, db_session):
        """测试无token登出"""
        response = client.post("/api/auth/logout")
        assert response.status_code == 401

    def test_token_blacklisted_after_logout(self, db_session, test_user, auth_headers, auth_token):
        """测试登出后token被加入黑名单"""
        # 登出
        client.post("/api/auth/logout", headers=auth_headers)
        
        # 尝试使用相同token访问受保护路由
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 401
        assert "revoked" in response.json()["detail"].lower() or "blacklisted" in response.json()["detail"].lower()

    def test_logout_all_devices(self, db_session, test_user):
        """测试登出所有设备"""
        # 创建多个登录会话
        tokens = []
        for _ in range(3):
            response = client.post(
                "/api/auth/login",
                json={
                    "username": test_user.email,
                    "password": "TestPass123!"
                }
            )
            tokens.append(response.json()["access_token"])
        
        # 使用第一个token登出所有设备
        response = client.post(
            "/api/auth/logout/all",
            headers={"Authorization": f"Bearer {tokens[0]}"}
        )
        assert response.status_code == 200
        
        # 验证所有token都无效
        for token in tokens:
            response = client.get(
                "/api/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 401


class TestPasswordSecurity:
    """密码安全测试"""

    def test_password_hashing(self):
        """测试密码哈希"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 50
        assert verify_password(password, hashed)
        assert not verify_password("WrongPassword", hashed)

    def test_password_complexity_requirements(self, db_session):
        """测试密码复杂度要求"""
        weak_passwords = [
            "123456",
            "password",
            "abc123",
            "12345678",
            "qwerty"
        ]
        
        for weak_pass in weak_passwords:
            response = client.post(
                "/api/auth/register",
                json={
                    "email": f"test_{weak_pass}@example.com",
                    "password": weak_pass,
                    "password_confirm": weak_pass,
                    "username": f"user_{weak_pass}"
                }
            )
            assert response.status_code == 422

    def test_password_history(self, db_session, test_user, auth_headers):
        """测试密码历史（不能使用最近使用过的密码）"""
        old_passwords = ["OldPass1!", "OldPass2!", "OldPass3!"]
        
        # 多次更改密码
        for password in old_passwords:
            client.post(
                "/api/users/change-password",
                headers=auth_headers,
                json={
                    "current_password": "TestPass123!",
                    "new_password": password,
                    "new_password_confirm": password
                }
            )
        
        # 尝试使用旧密码
        response = client.post(
            "/api/users/change-password",
            headers=auth_headers,
            json={
                "current_password": old_passwords[-1],
                "new_password": old_passwords[0],
                "new_password_confirm": old_passwords[0]
            }
        )
        assert response.status_code == 400
        assert "recently used" in response.json()["detail"].lower()


# Fixtures

@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPass123!"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_with_phone(db_session):
    """创建带手机号的测试用户"""
    user = User(
        phone="13800138000",
        username="phoneuser",
        hashed_password=get_password_hash("TestPass123!"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def inactive_user(db_session):
    """创建未激活用户"""
    user = User(
        email="inactive@example.com",
        username="inactiveuser",
        hashed_password=get_password_hash("TestPass123!"),
        is_active=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """生成认证token"""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": str(test_user.id), "email": test_user.email})


@pytest.fixture
def auth_headers(auth_token):
    """生成认证请求头"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def expired_token(test_user):
    """生成过期token"""
    from app.core.security import create_access_token
    return create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email},
        expires_delta=timedelta(minutes=-10)
    )


@pytest.fixture
def password_reset_token(test_user):
    """生成密码重置token"""
    from app.core.security import create_password_reset_token
    return create_password_reset_token(test_user.email)


@pytest.fixture
def expired_reset_token(test_user):
    """生成过期的重置token"""
    from app.core.security import create_password_reset_token
    return create_password_reset_token(
        test_user.email,
        expires_delta=timedelta(minutes=-10)
    )
