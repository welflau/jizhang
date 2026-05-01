from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    avatar: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度至少为6位')
        return v


class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    avatar: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


class UserPasswordChange(BaseModel):
    """用户密码修改模型"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v

    @validator('new_password')
    def validate_new_password(cls, v, values):
        if 'old_password' in values and v == values['old_password']:
            raise ValueError('新密码不能与旧密码相同')
        if len(v) < 6:
            raise ValueError('密码长度至少为6位')
        return v


class UserPreferences(BaseModel):
    """用户偏好设置模型"""
    theme: Optional[str] = Field("light", description="主题设置: light/dark")
    language: Optional[str] = Field("zh-CN", description="语言设置")
    notification_enabled: Optional[bool] = Field(True, description="是否启用通知")
    email_notification: Optional[bool] = Field(True, description="是否启用邮件通知")
    timezone: Optional[str] = Field("Asia/Shanghai", description="时区设置")


class UserPreferencesUpdate(BaseModel):
    """用户偏好设置更新模型"""
    theme: Optional[str] = Field(None, description="主题设置: light/dark")
    language: Optional[str] = Field(None, description="语言设置")
    notification_enabled: Optional[bool] = Field(None, description="是否启用通知")
    email_notification: Optional[bool] = Field(None, description="是否启用邮件通知")
    timezone: Optional[str] = Field(None, description="时区设置")


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: int
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime
    preferences: Optional[UserPreferences] = None

    class Config:
        from_attributes = True
        orm_mode = True


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    preferences: Optional[UserPreferences] = None

    class Config:
        from_attributes = True
        orm_mode = True


class UserProfile(BaseModel):
    """用户个人资料完整模型"""
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    preferences: Optional[UserPreferences] = None
    statistics: Optional[dict] = None  # 用户统计信息（如文章数、评论数等）

    class Config:
        from_attributes = True
        orm_mode = True


class Token(BaseModel):
    """Token模型"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token数据模型"""
    username: Optional[str] = None
    user_id: Optional[int] = None