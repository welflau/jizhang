from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserPreferenceBase(BaseModel):
    """用户偏好设置基础模型"""
    theme: Optional[str] = Field(default="light", description="主题设置: light/dark/auto")
    language: Optional[str] = Field(default="zh-CN", description="语言设置")
    notification_enabled: Optional[bool] = Field(default=True, description="是否启用通知")
    email_notification: Optional[bool] = Field(default=True, description="是否启用邮件通知")
    timezone: Optional[str] = Field(default="Asia/Shanghai", description="时区设置")
    date_format: Optional[str] = Field(default="YYYY-MM-DD", description="日期格式")
    time_format: Optional[str] = Field(default="24h", description="时间格式: 12h/24h")
    page_size: Optional[int] = Field(default=20, ge=10, le=100, description="每页显示数量")
    auto_save: Optional[bool] = Field(default=True, description="是否自动保存")
    show_tutorial: Optional[bool] = Field(default=True, description="是否显示新手引导")


class UserPreferenceCreate(UserPreferenceBase):
    """创建用户偏好设置"""
    pass


class UserPreferenceUpdate(BaseModel):
    """更新用户偏好设置"""
    theme: Optional[str] = None
    language: Optional[str] = None
    notification_enabled: Optional[bool] = None
    email_notification: Optional[bool] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    page_size: Optional[int] = Field(default=None, ge=10, le=100)
    auto_save: Optional[bool] = None
    show_tutorial: Optional[bool] = None


class UserPreferenceInDB(UserPreferenceBase):
    """数据库中的用户偏好设置"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPreferenceResponse(UserPreferenceBase):
    """用户偏好设置响应模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True