import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt
from app.main import app
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings

client = TestClient(app)


class TestUserRegistration:
    """测试用户注册功能"""

    def test_register_with_email_success(self):
        """测试邮箱注册成功"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "password" not in data

    def test_register_with_phone_success(self):
        """测试手机号注册成功"""
        response = client.post(
            "/api/auth/register",
            json={
                "phone": "13800138000",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["phone"] == "13800138000"

    def test_register_duplicate_email(self):
        """测试重复邮箱注册"""
        user_data = {
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!"
        }
        client.post("/api/auth/register", json=user_data)
        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_register_password_mismatch(self):
        """测试密码不匹配"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "mismatch@example.com",
                "password": "SecurePass123!",
                "confirm_password": "DifferentPass123!"
            }
        )
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()

    def test_register_weak_password(self):
        """测试弱密码"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "weak@example.com",
                "password": "123",
                "confirm_password": "123"
            }
        )
        assert response.status_code == 400

    def test_register_invalid_email(self):
        """测试无效邮箱格式"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!"
            }
        )
        assert response.status_code == 422


class TestUserLogin:
    """测试用户登录功能"""

    def setup_method(self):
        """每个测试前创建测试用户"""
        self.test_user = {
            "email": "login@example.com",
            "password": "SecurePass123!"
        }
        client.post(
            "/api/auth/register",
            json={
                **self.test_user,
                "confirm_password": self.test_user["password"]
            }
        )

    def test_login_success(self):
        """测试登录成功"""
        response = client.post(
            "/api/auth/login",
            json=self.test_user
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_remember_me(self):
        """测试记住登录状态"""
        response = client.post(
            "/api/auth/login",
            json={
                **self.test_user,
                "remember_me": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        # 验证token过期时间更长
        token = data["access_token"]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"])
        assert exp > datetime.utcnow() + timedelta(days=7)

    def test_login_wrong_password(self):
        """测试错误密码"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": self.test_user["email"],
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self):
        """测试不存在的用户"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == 401

    def test_login_with_phone(self):
        """测试手机号登录"""
        # 先注册手机号用户
        phone_user = {
            "phone": "13900139000",
            "password": "SecurePass123!"
        }
        client.post(
            "/api/auth/register",
            json={
                **phone_user,
                "confirm_password": phone_user["password"]
            }
        )
        
        response = client.post(
            "/api/auth/login",
            json=phone_user
        )
        assert response.status_code == 200
        assert "access_token" in response.json()


class TestPasswordReset:
    """测试密码找回/重置功能"""

    def setup_method(self):
        """创建测试用户"""
        self.test_user = {
            "email": "reset@example.com",
            "password": "OldPassword123!"
        }
        client.post(
            "/api/auth/register",
            json={
                **self.test_user,
                "confirm_password": self.test_user["password"]
            }
        )

    def test_request_password_reset(self):
        """测试请求密码重置"""
        response = client.post(
            "/api/auth/password-reset/request",
            json={"email": self.test_user["email"]}
        )
        assert response.status_code == 200
        assert "reset link sent" in response.json()["message"].lower()

    def test_request_password_reset_nonexistent_email(self):
        """测试不存在的邮箱请求重置"""
        response = client.post(
            "/api/auth/password-reset/request",
            json={"email": "nonexistent@example.com"}
        )
        # 出于安全考虑，应返回相同响应
        assert response.status_code == 200

    def test_reset_password_with_valid_token(self):
        """测试使用有效token重置密码"""
        # 先请求重置
        client.post(
            "/api/auth/password-reset/request",
            json={"email": self.test_user["email"]}
        )
        
        # 模拟获取重置token（实际应从邮件中获取）
        reset_token = create_access_token(
            data={"sub": self.test_user["email"], "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": reset_token,
                "new_password": "NewPassword123!",
                "confirm_password": "NewPassword123!"
            }
        )
        assert response.status_code == 200
        
        # 验证可以用新密码登录
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": self.test_user["email"],
                "password": "NewPassword123!"
            }
        )
        assert login_response.status_code == 200

    def test_reset_password_with_expired_token(self):
        """测试使用过期token重置密码"""
        expired_token = create_access_token(
            data={"sub": self.test_user["email"], "type": "password_reset"},
            expires_delta=timedelta(seconds=-1)
        )
        
        response = client.post(
            "/api/auth/password-reset/confirm",
            json={
                "token": expired_token,
                "new_password": "NewPassword123!",
                "confirm_password": "NewPassword123!"
            }
        )
        assert response.status_code == 401


class TestJWTAuthentication:
    """测试JWT认证功能"""

    def setup_method(self):
        """创建测试用户并登录"""
        self.test_user = {
            "email": "jwt@example.com",
            "password": "SecurePass123!"
        }
        client.post(
            "/api/auth/register",
            json={
                **self.test_user,
                "confirm_password": self.test_user["password"]
            }
        )
        
        login_response = client.post("/api/auth/login", json=self.test_user)
        self.access_token = login_response.json()["access_token"]

    def test_access_protected_route_with_valid_token(self):
        """测试使用有效token访问受保护路由"""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == self.test_user["email"]

    def test_access_protected_route_without_token(self):
        """测试无token访问受保护路由"""
        response = client.get("/api/users/me")
        assert response.status_code == 401

    def test_access_protected_route_with_invalid_token(self):
        """测试使用无效token访问受保护路由"""
        response = client.get(
            "/api/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_refresh_token(self):
        """测试刷新token"""
        login_response = client.post("/api/auth/login", json=self.test_user)
        refresh_token = login_response.json()["refresh_token"]
        
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()


class TestLogout:
    """测试登出功能"""

    def setup_method(self):
        """创建测试用户并登录"""
        self.test_user = {
            "email": "logout@example.com",
            "password": "SecurePass123!"
        }
        client.post(
            "/api/auth/register",
            json={
                **self.test_user,
                "confirm_password": self.test_user["password"]
            }
        )
        
        login_response = client.post("/api/auth/login", json=self.test_user)
        self.access_token = login_response.json()["access_token"]

    def test_logout_success(self):
        """测试登出成功"""
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

    def test_logout_invalidates_token(self):
        """测试登出后token失效"""
        client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        # 尝试使用已登出的token访问受保护路由
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 401


class TestPasswordSecurity:
    """测试密码安全功能"""

    def test_password_hashing(self):
        """测试密码加密"""
        password = "SecurePass123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 50
        assert verify_password(password, hashed)

    def test_password_verification(self):
        """测试密码验证"""
        password = "SecurePass123!"
        wrong_password = "WrongPass123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed)
        assert not verify_password(wrong_password, hashed)

    def test_same_password_different_hashes(self):
        """测试相同密码生成不同哈希值（salt）"""
        password = "SecurePass123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestTokenGeneration:
    """测试Token生成功能"""

    def test_create_access_token(self):
        """测试创建访问token"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert token is not None
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "test@example.com"
        assert "exp" in payload

    def test_token_expiration(self):
        """测试token过期时间"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        
        assert exp > now
        assert exp < now + timedelta(minutes=31)
