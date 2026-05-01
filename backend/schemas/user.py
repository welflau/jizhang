from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
import re

class UpdateUserInfoRequest(BaseModel):
    """Request schema for updating user information"""
    nickname: Optional[str] = Field(None, min_length=1, max_length=100, description="User nickname")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")
    current_password: Optional[str] = Field(None, min_length=6, description="Current password for verification")
    new_password: Optional[str] = Field(None, min_length=6, max_length=128, description="New password")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences as JSON object")

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("nickname cannot be empty or whitespace only")
            if len(v) > 100:
                raise ValueError("nickname too long (max 100 characters)")
        return v

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) < 6:
                raise ValueError("new password must be at least 6 characters")
            if len(v) > 128:
                raise ValueError("new password too long (max 128 characters)")
            # Password strength check: at least one letter and one number
            if not re.search(r"[a-zA-Z]", v) or not re.search(r"\d", v):
                raise ValueError("new password must contain at least one letter and one number")
        return v

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v and not (v.startswith("http://") or v.startswith("https://") or v.startswith("/")):
                raise ValueError("avatar_url must be a valid URL or path")
        return v

class UserResponse(BaseModel):
    """Response schema for user information"""
    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True