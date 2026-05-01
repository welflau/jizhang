from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    """用户基础模型"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    username: str = Field(..., min_length=3, max_length=50)

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            # 验证手机号格式（中国大陆）
            pattern = r'^1[3-9]\d{9}$'
            if not re.match(pattern, v):
                raise ValueError('手机号格式不正确')
        return v

    @validator('username')
    def validate_username(cls, v):
        # 用户名只能包含字母、数字、下划线
        pattern = r'^[a-zA-Z0-9_]+$'
        if not re.match(pattern, v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v


class UserRegister(UserBase):
    """用户注册模型"""
    password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str = Field(..., min_length=6, max_length=128)

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v

    @validator('password')
    def validate_password(cls, v):
        # 密码强度验证：至少包含一个字母和一个数字
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "phone": "13800138000",
                "username": "testuser",
                "password": "password123",
                "confirm_password": "password123"
            }
        }


class UserLogin(BaseModel):
    """用户登录模型"""
    login_id: str = Field(..., description="邮箱或手机号")
    password: str = Field(..., min_length=6)
    remember_me: bool = Field(default=False, description="记住登录状态")

    class Config:
        json_schema_extra = {
            "example": {
                "login_id": "user@example.com",
                "password": "password123",
                "remember_me": True
            }
        }


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    email: Optional[str] = None
    phone: Optional[str] = None
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "phone": "13800138000",
                "username": "testuser",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


class Token(BaseModel):
    """Token 响应模型"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = Field(..., description="过期时间（秒）")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class TokenData(BaseModel):
    """Token 数据模型"""
    user_id: Optional[int] = None
    username: Optional[str] = None


class PasswordReset(BaseModel):
    """密码重置请求模型"""
    login_id: str = Field(..., description="邮箱或手机号")

    class Config:
        json_schema_extra = {
            "example": {
                "login_id": "user@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """密码重置确认模型"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str = Field(..., min_length=6, max_length=128)

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v

    @validator('new_password')
    def validate_password(cls, v):
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "token": "reset_token_here",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123"
            }
        }


class PasswordChange(BaseModel):
    """密码修改模型"""
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str = Field(..., min_length=6, max_length=128)

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
            raise ValueError('密码必须包含至少一个字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含至少一个数字')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "oldpassword123",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123"
            }
        }


class RefreshToken(BaseModel):
    """刷新 Token 模型"""
    refresh_token: str = Field(..., description="刷新令牌")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class UserUpdate(BaseModel):
    """用户信息更新模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            pattern = r'^1[3-9]\d{9}$'
            if not re.match(pattern, v):
                raise ValueError('手机号格式不正确')
        return v

    @validator('username')
    def validate_username(cls, v):
        if v:
            pattern = r'^[a-zA-Z0-9_]+$'
            if not re.match(pattern, v):
                raise ValueError('用户名只能包含字母、数字和下划线')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "newusername",
                "email": "newemail@example.com",
                "phone": "13900139000"
            }
        }