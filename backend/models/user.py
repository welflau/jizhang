from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
import re

class UserPreferences(BaseModel):
    """User preference settings"""
    theme: str = Field(default="light", description="UI theme: light/dark")
    language: str = Field(default="en", description="Interface language")
    notifications_enabled: bool = Field(default=True, description="Enable notifications")
    email_notifications: bool = Field(default=True, description="Enable email notifications")

    class Config:
        json_schema_extra = {
            "example": {
                "theme": "dark",
                "language": "zh",
                "notifications_enabled": True,
                "email_notifications": False
            }
        }

class UserUpdateRequest(BaseModel):
    """User profile update request schema"""
    nickname: Optional[str] = Field(None, min_length=2, max_length=50, description="User nickname")
    avatar: Optional[str] = Field(None, max_length=500, description="Avatar URL")
    current_password: Optional[str] = Field(None, description="Current password for verification")
    new_password: Optional[str] = Field(None, min_length=8, max_length=128, description="New password")
    preferences: Optional[UserPreferences] = Field(None, description="User preferences")

    @validator('avatar')
    def validate_avatar_url(cls, v):
        if v is None:
            return v
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not url_pattern.match(v):
            raise ValueError('Invalid avatar URL format')
        return v

    @validator('new_password')
    def validate_password_strength(cls, v):
        if v is None:
            return v
        # Password must contain at least one uppercase, one lowercase, one digit
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "nickname": "JohnDoe",
                "avatar": "https://example.com/avatar.jpg",
                "current_password": "OldPass123",
                "new_password": "NewPass456",
                "preferences": {
                    "theme": "dark",
                    "language": "en"
                }
            }
        }

class UserResponse(BaseModel):
    """User profile response schema"""
    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    preferences: Optional[dict] = None
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "nickname": "JohnDoe",
                "avatar": "https://example.com/avatar.jpg",
                "preferences": {"theme": "dark", "language": "en"},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z"
            }
        }