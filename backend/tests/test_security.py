import pytest
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException, status
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password,
    decode_token,
)
from app.core.config import settings


class TestPasswordHashing:
    """测试密码哈希功能"""

    def test_password_hash(self):
        """测试密码哈希"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self):
        """测试验证正确密码"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """测试验证错误密码"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """测试相同密码生成不同哈希值"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestTokenGeneration:
    """测试 Token 生成功能"""

    def test_create_access_token(self):
        """测试创建访问令牌"""
        data = {"sub": "testuser@example.com", "user_id": 1}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiry(self):
        """测试创建自定义过期时间的访问令牌"""
        data = {"sub": "testuser@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)
        
        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        assert "exp" in decoded
        assert "sub" in decoded
        assert decoded["sub"] == "testuser@example.com"

    def test_create_refresh_token(self):
        """测试创建刷新令牌"""
        data = {"sub": "testuser@example.com", "user_id": 1}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_required_fields(self):
        """测试令牌包含必需字段"""
        data = {"sub": "testuser@example.com", "user_id": 1, "role": "user"}
        token = create_access_token(data)
        
        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        assert decoded["sub"] == "testuser@example.com"
        assert decoded["user_id"] == 1
        assert decoded["role"] == "user"
        assert "exp" in decoded


class TestTokenVerification:
    """测试 Token 验证功能"""

    def test_verify_valid_token(self):
        """测试验证有效令牌"""
        data = {"sub": "testuser@example.com", "user_id": 1}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "testuser@example.com"
        assert payload["user_id"] == 1

    def test_verify_invalid_token(self):
        """测试验证无效令牌"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in str(exc_info.value.detail)

    def test_verify_expired_token(self):
        """测试验证过期令牌"""
        data = {"sub": "testuser@example.com"}
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta=expires_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_verify_token_with_wrong_secret(self):
        """测试使用错误密钥验证令牌"""
        data = {"sub": "testuser@example.com"}
        
        # 使用错误的密钥创建令牌
        wrong_secret = "wrong_secret_key"
        token = jwt.encode(
            data,
            wrong_secret,
            algorithm=settings.ALGORITHM
        )
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_decode_token(self):
        """测试解码令牌"""
        data = {"sub": "testuser@example.com", "user_id": 1}
        token = create_access_token(data)
        
        payload = decode_token(token)
        
        assert payload["sub"] == "testuser@example.com"
        assert payload["user_id"] == 1

    def test_decode_invalid_token(self):
        """测试解码无效令牌"""
        invalid_token = "invalid.token.here"
        
        payload = decode_token(invalid_token)
        
        assert payload is None


class TestTokenExpiration:
    """测试 Token 过期功能"""

    def test_access_token_default_expiration(self):
        """测试访问令牌默认过期时间"""
        data = {"sub": "testuser@example.com"}
        token = create_access_token(data)
        
        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        now = datetime.utcnow()
        
        time_diff = exp_datetime - now
        
        # 默认过期时间应该接近配置的时间
        assert time_diff.total_seconds() > 0
        assert time_diff.total_seconds() <= settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60 + 5

    def test_refresh_token_longer_expiration(self):
        """测试刷新令牌有更长的过期时间"""
        data = {"sub": "testuser@example.com"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        access_decoded = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        refresh_decoded = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        access_exp = access_decoded["exp"]
        refresh_exp = refresh_decoded["exp"]
        
        assert refresh_exp > access_exp


class TestTokenPayload:
    """测试 Token 载荷"""

    def test_token_with_multiple_claims(self):
        """测试包含多个声明的令牌"""
        data = {
            "sub": "testuser@example.com",
            "user_id": 1,
            "role": "admin",
            "permissions": ["read", "write", "delete"]
        }
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload["sub"] == "testuser@example.com"
        assert payload["user_id"] == 1
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write", "delete"]

    def test_token_with_empty_subject(self):
        """测试空主题的令牌"""
        data = {"sub": ""}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload["sub"] == ""

    def test_token_with_special_characters(self):
        """测试包含特殊字符的令牌"""
        data = {
            "sub": "test+user@example.com",
            "name": "Test User (Admin)",
            "description": "User with special chars: !@#$%^&*()"
        }
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload["sub"] == "test+user@example.com"
        assert payload["name"] == "Test User (Admin)"
        assert "special chars" in payload["description"]


class TestSecurityEdgeCases:
    """测试安全边界情况"""

    def test_empty_password_hash(self):
        """测试空密码哈希"""
        password = ""
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_very_long_password(self):
        """测试超长密码"""
        password = "a" * 1000
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_unicode_password(self):
        """测试 Unicode 密码"""
        password = "密码测试🔐"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_token_without_subject(self):
        """测试没有主题的令牌"""
        data = {"user_id": 1}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload["user_id"] == 1

    def test_malformed_token_structure(self):
        """测试格式错误的令牌结构"""
        malformed_tokens = [
            "not.a.token",
            "only.two",
            "",
            "a" * 100,
        ]
        
        for token in malformed_tokens:
            with pytest.raises(HTTPException):
                verify_token(token)


class TestTokenRefresh:
    """测试令牌刷新功能"""

    def test_refresh_token_creation(self):
        """测试刷新令牌创建"""
        data = {"sub": "testuser@example.com", "user_id": 1}
        refresh_token = create_refresh_token(data)
        
        payload = verify_token(refresh_token)
        
        assert payload["sub"] == "testuser@example.com"
        assert payload["user_id"] == 1

    def test_refresh_token_different_from_access(self):
        """测试刷新令牌与访问令牌不同"""
        data = {"sub": "testuser@example.com"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        assert access_token != refresh_token
