import pytest
from datetime import datetime, timedelta
from jose import jwt
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
        """测试相同密码生成不同哈希值（因为盐值不同）"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """测试 JWT token 功能"""

    def test_create_access_token(self):
        """测试创建访问令牌"""
        user_id = 1
        token = create_access_token(user_id=user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """测试创建刷新令牌"""
        user_id = 1
        token = create_refresh_token(user_id=user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        """测试解码访问令牌"""
        user_id = 1
        token = create_access_token(user_id=user_id)
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_decode_refresh_token(self):
        """测试解码刷新令牌"""
        user_id = 1
        token = create_refresh_token(user_id=user_id)
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_verify_valid_token(self):
        """测试验证有效令牌"""
        user_id = 1
        token = create_access_token(user_id=user_id)
        
        result = verify_token(token, token_type="access")
        assert result is not None
        assert result == user_id

    def test_verify_invalid_token(self):
        """测试验证无效令牌"""
        invalid_token = "invalid.token.here"
        
        result = verify_token(invalid_token, token_type="access")
        assert result is None

    def test_verify_expired_token(self):
        """测试验证过期令牌"""
        user_id = 1
        # 创建一个已过期的令牌
        expires_delta = timedelta(seconds=-1)
        payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": datetime.utcnow() + expires_delta
        }
        expired_token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        result = verify_token(expired_token, token_type="access")
        assert result is None

    def test_verify_wrong_token_type(self):
        """测试验证错误类型的令牌"""
        user_id = 1
        access_token = create_access_token(user_id=user_id)
        
        # 使用 access token 验证 refresh token
        result = verify_token(access_token, token_type="refresh")
        assert result is None

    def test_token_with_additional_claims(self):
        """测试带有额外声明的令牌"""
        user_id = 1
        additional_claims = {"role": "admin", "email": "test@example.com"}
        token = create_access_token(user_id=user_id, additional_claims=additional_claims)
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["role"] == "admin"
        assert payload["email"] == "test@example.com"

    def test_access_token_expiration_time(self):
        """测试访问令牌过期时间"""
        user_id = 1
        token = create_access_token(user_id=user_id)
        payload = decode_token(token)
        
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        now = datetime.utcnow()
        
        # 验证过期时间大约是配置的时间（允许几秒误差）
        expected_expiration = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        time_diff = abs((exp_datetime - expected_expiration).total_seconds())
        assert time_diff < 5  # 允许5秒误差

    def test_refresh_token_expiration_time(self):
        """测试刷新令牌过期时间"""
        user_id = 1
        token = create_refresh_token(user_id=user_id)
        payload = decode_token(token)
        
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        now = datetime.utcnow()
        
        # 验证过期时间大约是配置的时间
        expected_expiration = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        time_diff = abs((exp_datetime - expected_expiration).total_seconds())
        assert time_diff < 5  # 允许5秒误差

    def test_decode_invalid_token(self):
        """测试解码无效令牌"""
        invalid_token = "invalid.token.here"
        payload = decode_token(invalid_token)
        
        assert payload is None

    def test_token_contains_required_fields(self):
        """测试令牌包含必需字段"""
        user_id = 1
        token = create_access_token(user_id=user_id)
        payload = decode_token(token)
        
        assert "sub" in payload
        assert "exp" in payload
        assert "type" in payload
        assert "iat" in payload  # issued at

    def test_different_users_different_tokens(self):
        """测试不同用户生成不同令牌"""
        token1 = create_access_token(user_id=1)
        token2 = create_access_token(user_id=2)
        
        assert token1 != token2
        
        payload1 = decode_token(token1)
        payload2 = decode_token(token2)
        
        assert payload1["sub"] != payload2["sub"]


class TestSecurityEdgeCases:
    """测试安全边界情况"""

    def test_empty_password(self):
        """测试空密码"""
        password = ""
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_very_long_password(self):
        """测试超长密码"""
        password = "a" * 1000
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_special_characters_password(self):
        """测试特殊字符密码"""
        password = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_unicode_password(self):
        """测试 Unicode 密码"""
        password = "密码测试🔐"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_token_with_zero_user_id(self):
        """测试用户 ID 为 0 的令牌"""
        user_id = 0
        token = create_access_token(user_id=user_id)
        result = verify_token(token, token_type="access")
        
        assert result == user_id

    def test_token_with_negative_user_id(self):
        """测试负数用户 ID 的令牌"""
        user_id = -1
        token = create_access_token(user_id=user_id)
        result = verify_token(token, token_type="access")
        
        assert result == user_id

    def test_token_with_large_user_id(self):
        """测试大数字用户 ID 的令牌"""
        user_id = 999999999
        token = create_access_token(user_id=user_id)
        result = verify_token(token, token_type="access")
        
        assert result == user_id

    def test_malformed_token_parts(self):
        """测试格式错误的令牌"""
        malformed_tokens = [
            "only.two.parts",
            "too.many.parts.here.extra",
            "no-dots-at-all",
            "",
            "...",
        ]
        
        for token in malformed_tokens:
            result = verify_token(token, token_type="access")
            assert result is None

    def test_token_with_wrong_signature(self):
        """测试签名错误的令牌"""
        user_id = 1
        token = create_access_token(user_id=user_id)
        
        # 修改令牌的最后一个字符来破坏签名
        tampered_token = token[:-1] + ("a" if token[-1] != "a" else "b")
        
        result = verify_token(tampered_token, token_type="access")
        assert result is None

    def test_token_without_type_claim(self):
        """测试没有 type 声明的令牌"""
        user_id = 1
        payload = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        result = verify_token(token, token_type="access")
        assert result is None

    def test_token_without_sub_claim(self):
        """测试没有 sub 声明的令牌"""
        payload = {
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        result = verify_token(token, token_type="access")
        assert result is None
