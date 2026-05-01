from typing import Optional
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for all API exceptions"""
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str = "Internal server error",
        code: str = "INTERNAL_ERROR",
        data: Optional[dict] = None
    ):
        self.status_code = status_code
        self.message = message
        self.code = code
        self.data = data
        super().__init__(status_code=status_code, detail=message)


class NotFoundError(BaseAPIException):
    """Resource not found exception"""
    
    def __init__(self, message: str = "Resource not found", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            code="NOT_FOUND",
            data=data
        )


class ValidationError(BaseAPIException):
    """Validation error exception"""
    
    def __init__(self, message: str = "Validation error", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            code="VALIDATION_ERROR",
            data=data
        )


class UnauthorizedError(BaseAPIException):
    """Unauthorized access exception"""
    
    def __init__(self, message: str = "Unauthorized", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            code="UNAUTHORIZED",
            data=data
        )


class ForbiddenError(BaseAPIException):
    """Forbidden access exception"""
    
    def __init__(self, message: str = "Forbidden", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            code="FORBIDDEN",
            data=data
        )


class BadRequestError(BaseAPIException):
    """Bad request exception"""
    
    def __init__(self, message: str = "Bad request", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            code="BAD_REQUEST",
            data=data
        )


class ConflictError(BaseAPIException):
    """Conflict exception (e.g., duplicate resource)"""
    
    def __init__(self, message: str = "Resource conflict", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            code="CONFLICT",
            data=data
        )


class InternalServerError(BaseAPIException):
    """Internal server error exception"""
    
    def __init__(self, message: str = "Internal server error", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            code="INTERNAL_ERROR",
            data=data
        )


class ServiceUnavailableError(BaseAPIException):
    """Service unavailable exception"""
    
    def __init__(self, message: str = "Service unavailable", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message=message,
            code="SERVICE_UNAVAILABLE",
            data=data
        )


class DatabaseError(BaseAPIException):
    """Database operation error exception"""
    
    def __init__(self, message: str = "Database error", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            code="DATABASE_ERROR",
            data=data
        )


class AuthenticationError(BaseAPIException):
    """Authentication error exception"""
    
    def __init__(self, message: str = "Authentication failed", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            code="AUTHENTICATION_ERROR",
            data=data
        )


class TokenExpiredError(BaseAPIException):
    """Token expired exception"""
    
    def __init__(self, message: str = "Token has expired", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            code="TOKEN_EXPIRED",
            data=data
        )


class InvalidTokenError(BaseAPIException):
    """Invalid token exception"""
    
    def __init__(self, message: str = "Invalid token", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            code="INVALID_TOKEN",
            data=data
        )


class PermissionDeniedError(BaseAPIException):
    """Permission denied exception"""
    
    def __init__(self, message: str = "Permission denied", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            code="PERMISSION_DENIED",
            data=data
        )


class RateLimitError(BaseAPIException):
    """Rate limit exceeded exception"""
    
    def __init__(self, message: str = "Rate limit exceeded", data: Optional[dict] = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            data=data
        )