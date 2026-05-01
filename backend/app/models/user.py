from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=11, max_length=11)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('invalid phone number format')
        return v


class UserCreate(UserBase):
    """Schema for user registration request."""
    password: str = Field(min_length=8, max_length=128)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('password must contain at least one digit')
        return v

    def model_post_init(self, __context) -> None:
        """Ensure at least one of email or phone is provided."""
        if not self.email and not self.phone:
            raise ValueError('either email or phone must be provided')


class UserInDB(UserBase):
    """User model as stored in database."""
    id: int
    hashed_password: str
    created_at: datetime
    is_active: bool = True


class UserResponse(UserBase):
    """Public user response schema (no sensitive data)."""
    id: int
    created_at: datetime
    is_active: bool


class LoginRequest(BaseModel):
    """Schema for login request."""
    identifier: str = Field(description="email or phone number")
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="token expiration time in seconds")
