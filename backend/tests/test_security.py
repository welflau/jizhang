import pytest
from datetime import timedelta
from jose import jwt
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_password,
    get_password_hash,
    decode_token,
)
from app.core.config import settings


class TestPasswordHashing:
    """测试密码哈希功能"""

    def test_hash_password(self):
        """测试密码哈希"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        """测试验证正确密码"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """测试验证错误密码"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """测试相同密码生成不同哈希值（因为salt不同）"""
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """测试JWT token功能"""

    def test_create_access_token(self):
        """测试创建访问token"""
        data = {"sub": "test_user", "user_id": 1}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expires(self):
        """测试创建带自定义过期时间的访问token"""
        data = {"sub": "test_user"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)
        
        assert token is not None
        
        # 解码验证过期时间
        payload = decode_token(token)
        assert payload is not None
        assert "exp" in payload

    def test_create_refresh_token(self):
        """测试创建刷新token"""
        data = {"sub": "test_user", "user_id": 1}
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        """测试解码有效token"""
        data = {"sub": "test_user", "user_id": 1, "email": "test@example.com"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test_user"
        assert payload["user_id"] == 1
        assert payload["email"] == "test@example.com"
        assert "exp" in payload

    def test_decode_invalid_token(self):
        """测试解码无效token"""
        invalid_token = "invalid.token.here"
        
        payload = decode_token(invalid_token)
        
        assert payload is None

    def test_decode_expired_token(self):
        """测试解码过期token"""
        data = {"sub": "test_user"}
        expires_delta = timedelta(seconds=-1)  # 已过期
        token = create_access_token(data, expires_delta=expires_delta)
        
        payload = decode_token(token)
        
        assert payload is None

    def test_verify_valid_token(self):
        """测试验证有效token"""
        data = {"sub": "test_user", "user_id": 1}
        token = create_access_token(data)
        
        is_valid = verify_token(token)
        
        assert is_valid is True

    def test_verify_invalid_token(self):
        """测试验证无效token"""
        invalid_token = "invalid.token.here"
        
        is_valid = verify_token(invalid_token)
        
        assert is_valid is False

    def test_verify_expired_token(self):
        """测试验证过期token"""
        data = {"sub": "test_user"}
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta=expires_delta)
        
        is_valid = verify_token(token)
        
        assert is_valid is False

    def test_token_contains_all_claims(self):
        """测试token包含所有声明"""
        data = {
            "sub": "test_user",
            "user_id": 123,
            "email": "test@example.com",
            "role": "admin"
        }
        token = create_access_token(data)
        payload = decode_token(token)
        
        assert payload["sub"] == "test_user"
        assert payload["user_id"] == 123
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"

    def test_refresh_token_has_longer_expiry(self):
        """测试刷新token有更长的过期时间"""
        data = {"sub": "test_user"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)
        
        assert refresh_payload["exp"] > access_payload["exp"]


class TestTokenSecurity:
    """测试token安全性"""

    def test_token_with_tampered_signature(self):
        """测试被篡改签名的token"""
        data = {"sub": "test_user", "user_id": 1}
        token = create_access_token(data)
        
        # 篡改token的最后几个字符
        tampered_token = token[:-10] + "tampered00"
        
        is_valid = verify_token(tampered_token)
        assert is_valid is False

    def test_token_with_tampered_payload(self):
        """测试被篡改payload的token"""
        data = {"sub": "test_user", "user_id": 1}
        token = create_access_token(data)
        
        # 尝试手动修改payload
        parts = token.split('.')
        if len(parts) == 3:
            # 创建一个假的payload
            fake_payload = {"sub": "admin", "user_id": 999}
            import json
            import base64
            fake_payload_encoded = base64.urlsafe_b64encode(
                json.dumps(fake_payload).encode()
            ).decode().rstrip('=')
            
            tampered_token = f"{parts[0]}.{fake_payload_encoded}.{parts[2]}"
            
            is_valid = verify_token(tampered_token)
            assert is_valid is False

    def test_token_algorithm_verification(self):
        """测试token使用正确的算法"""
        data = {"sub": "test_user"}
        token = create_access_token(data)
        
        # 使用错误的算法尝试解码
        try:
            jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS512"]  # 错误的算法
            )
            assert False, "Should have raised an error"
        except jwt.JWTError:
            assert True

    def test_empty_token(self):
        """测试空token"""
        is_valid = verify_token("")
        assert is_valid is False
        
        payload = decode_token("")
        assert payload is None

    def test_none_token(self):
        """测试None token"""
        is_valid = verify_token(None)
        assert is_valid is False
        
        payload = decode_token(None)
        assert payload is None


class TestPasswordSecurity:
    """测试密码安全性"""

    def test_password_hash_length(self):
        """测试密码哈希长度"""
        password = "test"
        hashed = get_password_hash(password)
        
        # bcrypt哈希通常是60个字符
        assert len(hashed) == 60

    def test_empty_password_hash(self):
        """测试空密码哈希"""
        password = ""
        hashed = get_password_hash(password)
        
        assert len(hashed) > 0
        assert verify_password("", hashed) is True

    def test_long_password_hash(self):
        """测试长密码哈希"""
        password = "a" * 1000
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_special_characters_password(self):
        """测试包含特殊字符的密码"""
        password = "p@ssw0rd!#$%^&*()_+-=[]{}|;:',.<>?/~`"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_unicode_password(self):
        """测试Unicode密码"""
        password = "密码测试🔐"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True


class TestTokenEdgeCases:
    """测试token边界情况"""

    def test_token_with_special_characters_in_data(self):
        """测试数据中包含特殊字符的token"""
        data = {
            "sub": "user@example.com",
            "name": "Test User!@#",
            "description": "Special chars: <>&\"'"
        }
        token = create_access_token(data)
        payload = decode_token(token)
        
        assert payload["sub"] == data["sub"]
        assert payload["name"] == data["name"]
        assert payload["description"] == data["description"]

    def test_token_with_unicode_data(self):
        """测试包含Unicode数据的token"""
        data = {
            "sub": "用户",
            "name": "测试用户",
            "emoji": "🔐🚀"
        }
        token = create_access_token(data)
        payload = decode_token(token)
        
        assert payload["sub"] == data["sub"]
        assert payload["name"] == data["name"]
        assert payload["emoji"] == data["emoji"]

    def test_token_with_large_payload(self):
        """测试大payload的token"""
        data = {
            "sub": "test_user",
            "large_data": "x" * 10000
        }
        token = create_access_token(data)
        payload = decode_token(token)
        
        assert payload["sub"] == data["sub"]
        assert len(payload["large_data"]) == 10000

    def test_multiple_tokens_independence(self):
        """测试多个token的独立性"""
        data1 = {"sub": "user1", "user_id": 1}
        data2 = {"sub": "user2", "user_id": 2}
        
        token1 = create_access_token(data1)
        token2 = create_access_token(data2)
        
        payload1 = decode_token(token1)
        payload2 = decode_token(token2)
        
        assert payload1["sub"] == "user1"
        assert payload2["sub"] == "user2"
        assert payload1["user_id"] == 1
        assert payload2["user_id"] == 2
