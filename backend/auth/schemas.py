from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class UserRegisterSchema(BaseModel):
    """用户注册模式"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str
    username: str = Field(..., min_length=3, max_length=50)

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

    @validator('password')
    def validate_password(cls, v):
        # 密码强度验证：至少包含数字、字母
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v

    @validator('username')
    def validate_username(cls, v):
        # 用户名只能包含字母、数字、下划线
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "phone": "13800138000",
                "password": "Password123",
                "confirm_password": "Password123",
                "username": "john_doe"
            }
        }


class UserLoginSchema(BaseModel):
    """用户登录模式"""
    identifier: str = Field(..., description="邮箱或手机号")
    password: str = Field(..., min_length=8)
    remember_me: bool = Field(default=False, description="记住登录状态")

    class Config:
        schema_extra = {
            "example": {
                "identifier": "user@example.com",
                "password": "Password123",
                "remember_me": True
            }
        }


class TokenSchema(BaseModel):
    """Token 响应模式"""
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


class TokenRefreshSchema(BaseModel):
    """Token 刷新模式"""
    refresh_token: str

    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class PasswordResetRequestSchema(BaseModel):
    """密码重置请求模式"""
    identifier: str = Field(..., description="邮箱或手机号")

    class Config:
        schema_extra = {
            "example": {
                "identifier": "user@example.com"
            }
        }


class PasswordResetVerifySchema(BaseModel):
    """密码重置验证模式"""
    identifier: str = Field(..., description="邮箱或手机号")
    verification_code: str = Field(..., min_length=6, max_length=6)

    class Config:
        schema_extra = {
            "example": {
                "identifier": "user@example.com",
                "verification_code": "123456"
            }
        }


class PasswordResetConfirmSchema(BaseModel):
    """密码重置确认模式"""
    identifier: str = Field(..., description="邮箱或手机号")
    verification_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v

    @validator('new_password')
    def validate_password(cls, v):
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v

    class Config:
        schema_extra = {
            "example": {
                "identifier": "user@example.com",
                "verification_code": "123456",
                "new_password": "NewPassword123",
                "confirm_password": "NewPassword123"
            }
        }


class PasswordChangeSchema(BaseModel):
    """密码修改模式（已登录用户）"""
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v

    @validator('new_password')
    def validate_password(cls, v, values):
        if 'old_password' in values and v == values['old_password']:
            raise ValueError('新密码不能与旧密码相同')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v

    class Config:
        schema_extra = {
            "example": {
                "old_password": "OldPassword123",
                "new_password": "NewPassword123",
                "confirm_password": "NewPassword123"
            }
        }


class UserResponseSchema(BaseModel):
    """用户响应模式"""
    id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "user@example.com",
                "phone": "13800138000",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class LoginResponseSchema(BaseModel):
    """登录响应模式"""
    user: UserResponseSchema
    token: TokenSchema

    class Config:
        schema_extra = {
            "example": {
                "user": {
                    "id": 1,
                    "username": "john_doe",
                    "email": "user@example.com",
                    "phone": "13800138000",
                    "is_active": True,
                    "is_verified": True,
                    "created_at": "2024-01-01T00:00:00"
                },
                "token": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 3600
                }
            }
        }


class MessageResponseSchema(BaseModel):
    """通用消息响应模式"""
    message: str
    detail: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "message": "操作成功",
                "detail": "详细信息"
            }
        }


class EmailVerificationSchema(BaseModel):
    """邮箱验证模式"""
    email: EmailStr
    verification_code: str = Field(..., min_length=6, max_length=6)

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "verification_code": "123456"
            }
        }


class PhoneVerificationSchema(BaseModel):
    """手机验证模式"""
    phone: str
    verification_code: str = Field(..., min_length=6, max_length=6)

    @validator('phone')
    def validate_phone(cls, v):
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, v):
            raise ValueError('手机号格式不正确')
        return v

    class Config:
        schema_extra = {
            "example": {
                "phone": "13800138000",
                "verification_code": "123456"
            }
        }