from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class RegisterRequest(BaseModel):
    """Request schema for user registration."""
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, max_length=100, description="Password (min 8 chars)")


class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Response schema for user data."""
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class PasswordResetRequest(BaseModel):
    """Request schema for password reset."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Request schema for confirming password reset."""
    token: str
    new_password: str = Field(min_length=8, max_length=100)