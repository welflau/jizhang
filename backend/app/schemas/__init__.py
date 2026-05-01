"""
Pydantic schemas for request/response validation.
Export all schema models for easy import.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# Base schemas
class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool = True
    message: str = "Operation successful"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Paginated response schema"""
    success: bool = True
    message: str = "Data retrieved successfully"
    data: List[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0


# Health check schemas
class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    environment: str = "development"


# Example user schemas (can be extended)
class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    """User update schema"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')


class UserResponse(UserBase):
    """User response schema"""
    id: int
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        }


# Export all schemas
__all__ = [
    "BaseResponse",
    "ErrorResponse",
    "PaginationParams",
    "PaginatedResponse",
    "HealthCheckResponse",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
]