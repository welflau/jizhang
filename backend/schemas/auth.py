from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class UserRegister(BaseModel):
    """用户注册请求模型"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str
    username: str = Field(..., min_length=2, max_length=50)

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            # 验证手机号格式（中国大陆）
            pattern = r'^1[3-9]\d{9}$'
            if not re.match(pattern, v):
                raise ValueError('手机号格式不正确')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v

    @validator('email', 'phone')
    def at_least_one_contact(cls, v, values):
        if not v and not values.get('email') and not values.get('phone'):
            raise ValueError('邮箱和手机号至少需要提供一个')
        return v

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "phone": "13800138000",
                "password": "SecurePass123",
                "confirm_password": "SecurePass123",
                "username": "张三"
            }
        }


class UserLogin(BaseModel):
    """用户登录请求模型"""
    account: str = Field(..., description="邮箱或手机号")
    password: str = Field(..., min_length=6)
    remember_me: bool = Field(default=False, description="记住登录状态")

    class Config:
        schema_extra = {
            "example": {
                "account": "user@example.com",
                "password": "SecurePass123",
                "remember_me": True
            }
        }


class Token(BaseModel):
    """Token 响应模型"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = Field(..., description="过期时间（秒）")

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class TokenPayload(BaseModel):
    """Token 载荷模型"""
    sub: str = Field(..., description="用户ID")
    exp: datetime = Field(..., description="过期时间")
    iat: datetime = Field(..., description="签发时间")
    type: str = Field(default="access", description="token类型: access/refresh")


class RefreshToken(BaseModel):
    """刷新 Token 请求模型"""
    refresh_token: str

    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class PasswordResetRequest(BaseModel):
    """密码重置请求模型"""
    account: str = Field(..., description="邮箱或手机号")

    class Config:
        schema_extra = {
            "example": {
                "account": "user@example.com"
            }
        }


class PasswordResetVerify(BaseModel):
    """密码重置验证模型"""
    account: str = Field(..., description="邮箱或手机号")
    verification_code: str = Field(..., min_length=4, max_length=6)
    new_password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v

    class Config:
        schema_extra = {
            "example": {
                "account": "user@example.com",
                "verification_code": "123456",
                "new_password": "NewSecurePass123",
                "confirm_password": "NewSecurePass123"
            }
        }


class PasswordChange(BaseModel):
    """修改密码模型（已登录用户）"""
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v

    @validator('new_password')
    def password_not_same(cls, v, values):
        if 'old_password' in values and v == values['old_password']:
            raise ValueError('新密码不能与旧密码相同')
        return v

    class Config:
        schema_extra = {
            "example": {
                "old_password": "OldPass123",
                "new_password": "NewSecurePass123",
                "confirm_password": "NewSecurePass123"
            }
        }


class UserResponse(BaseModel):
    """用户信息响应模型"""
    id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "phone": "13800138000",
                "username": "张三",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-01T00:00:00",
                "last_login": "2024-01-15T10:30:00"
            }
        }


class LoginResponse(BaseModel):
    """登录成功响应模型"""
    user: UserResponse
    token: Token

    class Config:
        schema_extra = {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "username": "张三",
                    "is_active": True,
                    "is_verified": True,
                    "created_at": "2024-01-01T00:00:00",
                    "last_login": "2024-01-15T10:30:00"
                },
                "token": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 3600
                }
            }
        }


class VerificationCodeRequest(BaseModel):
    """验证码请求模型"""
    account: str = Field(..., description="邮箱或手机号")
    type: str = Field(..., description="验证码类型: register/reset_password")

    @validator('type')
    def validate_type(cls, v):
        allowed_types = ['register', 'reset_password']
        if v not in allowed_types:
            raise ValueError(f'验证码类型必须是: {", ".join(allowed_types)}')
        return v

    class Config:
        schema_extra = {
            "example": {
                "account": "user@example.com",
                "type": "register"
            }
        }


class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str
    success: bool = True

    class Config:
        schema_extra = {
            "example": {
                "message": "操作成功",
                "success": True
            }
        }