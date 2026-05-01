import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.orm import Session

from backend.main import app
from backend.models.user import User
from backend.core.security import verify_password, get_password_hash
from backend.core.config import settings
from backend.database import get_db

client = TestClient(app)


class TestUserRegistration:
    """用户注册测试"""

    def test_register_with_email_success(self, db: Session):
        """测试邮箱注册成功"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
                "username": "testuser"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "id" in data
        assert "password" not in data

    def test_register_with_phone_success(self, db: Session):
        """测试手机号注册成功"""
        response = client.post(
            "/api/auth/register",
            json={
                "phone": "13800138000",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
                "username": "phoneuser"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["phone"] == "13800138000"
        assert data["username"] == "phoneuser"

    def test_register_duplicate_email(self, db: Session, test_user: User):
        """测试重复邮箱注册"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
                "username": "newuser"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_password_mismatch(self, db: Session):
        """测试密码不匹配"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test2@example.com",
                "password": "StrongPass123!",
                "confirm_password": "DifferentPass123!",
                "username": "testuser2"
            }
        )
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()

    def test_register_weak_password(self, db: Session):
        """测试弱密码"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test3@example.com",
                "password": "123",
                "confirm_password": "123",
                "username": "testuser3"
            }
        )
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()

    def test_register_invalid_email(self, db: Session):
        """测试无效邮箱格式"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
                "username": "testuser4"
            }
        )
        assert response.status_code == 422

    def test_register_invalid_phone(self, db: Session):
        """测试无效手机号格式"""
        response = client.post(
            "/api/auth/register",
            json={
                "phone": "123",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
                "username": "testuser5"
            }
        )
        assert response.status_code == 422

    def test_register_missing_credentials(self, db: Session):
        """测试缺少邮箱或手机号"""
        response = client.post(
            "/api/auth/register",
            json={
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
                "username": "testuser6"
            }
        )
        assert response.status_code == 400


class TestUserLogin:
    """用户登录测试"""

    def test_login_with_email_success(self, db: Session, test_user: User):
        """测试邮箱登录成功"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_login_with_phone_success(self, db: Session, test_user_phone: User):
        """测试手机号登录成功"""
        response = client.post(
            "/api/auth/login",
            json={
                "phone": "13800138000",
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_with_remember_me(self, db: Session, test_user: User):
        """测试记住登录状态"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "remember_me": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        # 验证 refresh_token 的过期时间更长
        refresh_token = data["refresh_token"]
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"])
        assert exp > datetime.utcnow() + timedelta(days=7)

    def test_login_wrong_password(self, db: Session, test_user: User):
        """测试错误密码"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, db: Session):
        """测试不存在的用户"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 401

    def test_login_inactive_user(self, db: Session, inactive_user: User):
        """测试未激活用户登录"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": inactive_user.email,
                "password": "TestPass123!"
            }
        )
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()


class TestJWTAuthentication:
    """JWT 认证测试"""

    def test_access_protected_route_with_valid_token(self, db: Session, auth_headers: dict):
        """测试使用有效 token 访问受保护路由"""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data

    def test_access_protected_route_without_token(self, db: Session):
        """测试无 token 访问受保护路由"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_access_protected_route_with_invalid_token(self, db: Session):
        """测试使用无效 token 访问受保护路由"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_access_protected_route_with_expired_token(self, db: Session, expired_token: str):
        """测试使用过期 token 访问受保护路由"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_refresh_token_success(self, db: Session, test_user: User):
        """测试刷新 token 成功"""
        # 先登录获取 refresh_token
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123!"
            }
        )
        refresh_token = login_response.json()["refresh_token"]

        # 使用 refresh_token 获取新的 access_token
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid(self, db: Session):
        """测试使用无效 refresh_token"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_refresh_token"}
        )
        assert response.status_code == 401


class TestPasswordReset:
    """密码重置测试"""

    def test_request_password_reset_success(self, db: Session, test_user: User):
        """测试请求密码重置成功"""
        response = client.post(
            "/api/auth/password-reset/request",
            json={"email": test_user.email}
        )
        assert response.status_code == 200
        assert "email sent" in response.json()["message"].lower()

    def test_request_password_reset_nonexistent_email(self, db: Session):
        """测试不存在的邮箱请求密码重置"""
        response = client.post(
            "/api/auth/password-reset/request",
            json={"email": "nonexistent@example.com"}
        )
        # 为了安全，即使邮箱不存在也返回成功
        assert response.status_code == 200

    def test_verify_reset_token_valid(self, db: Session, password_reset_token: str):
        """测试验证有效的重置 token"""
        response = client.get(
            f"/api/auth/password-reset/verify/{password_reset_token}"
        )
        assert response.status_code == 200

    def test_verify_reset_token_invalid(self, db: Session):
        """测试验证无效的重置 token"""
        response = client.get(
            "/api/auth/password-reset/verify/invalid_token"
        )
        assert response.status_code == 400

    def test_reset_password_success(self, db: Session, test_user: User, password_reset_token: str):
        """测试重置密码成功"""
        new_password = "NewStrongPass123!"
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": password_reset_token,
                "new_password": new_password,
                "confirm_password": new_password
            }
        )
        assert response.status_code == 200

        # 验证可以使用新密码登录
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": new_password
            }
        )
        assert login_response.status_code == 200

    def test_reset_password_mismatch(self, db: Session, password_reset_token: str):
        """测试重置密码不匹配"""
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": password_reset_token,
                "new_password": "NewPass123!",
                "confirm_password": "DifferentPass123!"
            }
        )
        assert response.status_code == 400

    def test_reset_password_expired_token(self, db: Session, expired_reset_token: str):
        """测试使用过期的重置 token"""
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": expired_reset_token,
                "new_password": "NewPass123!",
                "confirm_password": "NewPass123!"
            }
        )
        assert response.status_code == 400


class TestLogout:
    """登出功能测试"""

    def test_logout_success(self, db: Session, auth_headers: dict):
        """测试登出成功"""
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200

        # 验证 token 已失效
        me_response = client.get("/api/auth/me", headers=auth_headers)
        assert me_response.status_code == 401

    def test_logout_without_token(self, db: Session):
        """测试未登录状态下登出"""
        response = client.post("/api/auth/logout")
        assert response.status_code == 401

    def test_logout_all_devices(self, db: Session, test_user: User):
        """测试登出所有设备"""
        # 创建多个登录会话
        tokens = []
        for _ in range(3):
            login_response = client.post(
                "/api/auth/login",
                json={
                    "email": test_user.email,
                    "password": "TestPass123!"
                }
            )
            tokens.append(login_response.json()["access_token"])

        # 使用第一个 token 登出所有设备
        response = client.post(
            "/api/auth/logout-all",
            headers={"Authorization": f"Bearer {tokens[0]}"}
        )
        assert response.status_code == 200

        # 验证所有 token 都已失效
        for token in tokens:
            me_response = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert me_response.status_code == 401


class TestPasswordSecurity:
    """密码安全测试"""

    def test_password_hashing(self):
        """测试密码哈希"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed)

    def test_password_not_stored_plaintext(self, db: Session, test_user: User):
        """测试密码不以明文存储"""
        assert test_user.hashed_password != "TestPass123!"
        assert verify_password("TestPass123!", test_user.hashed_password)

    def test_different_hashes_for_same_password(self):
        """测试相同密码生成不同哈希"""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestChangePassword:
    """修改密码测试"""

    def test_change_password_success(self, db: Session, auth_headers: dict, test_user: User):
        """测试修改密码成功"""
        response = client.post(
            "/api/auth/change-password",
            headers=auth_headers,
            json={
                "old_password": "TestPass123!",
                "new_password": "NewStrongPass123!",
                "confirm_password": "NewStrongPass123!"
            }
        )
        assert response.status_code == 200

        # 验证可以使用新密码登录
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "NewStrongPass123!"
            }
        )
        assert login_response.status_code == 200

    def test_change_password_wrong_old_password(self, db: Session, auth_headers: dict):
        """测试旧密码错误"""
        response = client.post(
            "/api/auth/change-password",
            headers=auth_headers,
            json={
                "old_password": "WrongOldPass123!",
                "new_password": "NewStrongPass123!",
                "confirm_password": "NewStrongPass123!"
            }
        )
        assert response.status_code == 400

    def test_change_password_mismatch(self, db: Session, auth_headers: dict):
        """测试新密码不匹配"""
        response = client.post(
            "/api/auth/change-password",
            headers=auth_headers,
            json={
                "old_password": "TestPass123!",
                "new_password": "NewPass123!",
                "confirm_password": "DifferentPass123!"
            }
        )
        assert response.status_code == 400

    def test_change_password_same_as_old(self, db: Session, auth_headers: dict):
        """测试新密码与旧密码相同"""
        response = client.post(
            "/api/auth/change-password",
            headers=auth_headers,
            json={
                "old_password": "TestPass123!",
                "new_password": "TestPass123!",
                "confirm_password": "TestPass123!"
            }
        )
        assert response.status_code == 400
        assert "same" in response.json()["detail"].lower()
