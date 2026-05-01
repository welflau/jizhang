from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import re

class UserPreferences(BaseModel):
    """User preference settings"""
    theme: Optional[str] = Field(default="light", description="UI theme: light/dark")
    language: Optional[str] = Field(default="zh-CN", description="Interface language")
    notifications_enabled: Optional[bool] = Field(default=True, description="Enable notifications")
    email_notifications: Optional[bool] = Field(default=False, description="Email notifications")
    
    class Config:
        json_schema_extra = {
            "example": {
                "theme": "dark",
                "language": "en-US",
                "notifications_enabled": True,
                "email_notifications": False
            }
        }

class UpdateUserRequest(BaseModel):
    """Request model for updating user information"""
    nickname: Optional[str] = Field(None, min_length=2, max_length=30, description="User nickname")
    avatar: Optional[str] = Field(None, max_length=500, description="Avatar URL or base64 data")
    old_password: Optional[str] = Field(None, min_length=6, description="Current password (required for password change)")
    new_password: Optional[str] = Field(None, min_length=6, max_length=128, description="New password")
    preferences: Optional[UserPreferences] = Field(None, description="User preferences")
    
    @validator('nickname')
    def validate_nickname(cls, v):
        if v is not None:
            if not re.match(r'^[\w\u4e00-\u9fa5\s-]+$', v):
                raise ValueError('nickname can only contain letters, numbers, Chinese characters, spaces and hyphens')
        return v
    
    @validator('avatar')
    def validate_avatar(cls, v):
        if v is not None:
            # Allow URL or base64 data URI
            if not (v.startswith('http://') or v.startswith('https://') or v.startswith('data:image/')):
                raise ValueError('avatar must be a valid URL or base64 data URI')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v, values):
        if v is not None:
            # Password strength check
            if not re.search(r'[A-Za-z]', v) or not re.search(r'\d', v):
                raise ValueError('new_password must contain both letters and numbers')
            # Require old_password when changing password
            if 'old_password' not in values or values['old_password'] is None:
                raise ValueError('old_password is required when changing password')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "nickname": "John Doe",
                "avatar": "https://example.com/avatar.jpg",
                "old_password": "oldpass123",
                "new_password": "newpass456",
                "preferences": {
                    "theme": "dark",
                    "language": "en-US"
                }
            }
        }

class UserResponse(BaseModel):
    """User information response model"""
    id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "johndoe",
                "nickname": "John Doe",
                "avatar": "https://example.com/avatar.jpg",
                "email": "john@example.com",
                "preferences": {"theme": "dark"},
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }

class UpdateUserResponse(BaseModel):
    """Response model for user update operation"""
    success: bool
    message: str
    user: UserResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "User information updated successfully",
                "user": {
                    "id": 1,
                    "username": "johndoe",
                    "nickname": "John Doe",
                    "avatar": "https://example.com/avatar.jpg"
                }
            }
        }