from typing import Optional
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for all API exceptions"""
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_ERROR",
        message: str = "Internal server error",
        detail: Optional[str] = None,
    ):
        self.code = code
        self.message = message
        super().__init__(status_code=status_code, detail=detail or message)


class NotFoundError(BaseAPIException):
    """Resource not found exception"""
    
    def __init__(
        self,
        message: str = "Resource not found",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=message,
            detail=detail,
        )


class ValidationError(BaseAPIException):
    """Validation error exception"""
    
    def __init__(
        self,
        message: str = "Validation error",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message=message,
            detail=detail,
        )


class UnauthorizedError(BaseAPIException):
    """Unauthorized access exception"""
    
    def __init__(
        self,
        message: str = "Unauthorized access",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            message=message,
            detail=detail,
        )


class ForbiddenError(BaseAPIException):
    """Forbidden access exception"""
    
    def __init__(
        self,
        message: str = "Forbidden access",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            message=message,
            detail=detail,
        )


class ConflictError(BaseAPIException):
    """Resource conflict exception"""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            message=message,
            detail=detail,
        )


class BadRequestError(BaseAPIException):
    """Bad request exception"""
    
    def __init__(
        self,
        message: str = "Bad request",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="BAD_REQUEST",
            message=message,
            detail=detail,
        )


class InternalServerError(BaseAPIException):
    """Internal server error exception"""
    
    def __init__(
        self,
        message: str = "Internal server error",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_ERROR",
            message=message,
            detail=detail,
        )


class DatabaseError(BaseAPIException):
    """Database operation error exception"""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="DATABASE_ERROR",
            message=message,
            detail=detail,
        )


class ServiceUnavailableError(BaseAPIException):
    """Service unavailable exception"""
    
    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="SERVICE_UNAVAILABLE",
            message=message,
            detail=detail,
        )


class RateLimitError(BaseAPIException):
    """Rate limit exceeded exception"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            detail=detail,
        )


class TokenExpiredError(UnauthorizedError):
    """Token expired exception"""
    
    def __init__(
        self,
        message: str = "Token has expired",
        detail: Optional[str] = None,
    ):
        super().__init__(message=message, detail=detail)
        self.code = "TOKEN_EXPIRED"


class InvalidTokenError(UnauthorizedError):
    """Invalid token exception"""
    
    def __init__(
        self,
        message: str = "Invalid token",
        detail: Optional[str] = None,
    ):
        super().__init__(message=message, detail=detail)
        self.code = "INVALID_TOKEN"


class DuplicateResourceError(ConflictError):
    """Duplicate resource exception"""
    
    def __init__(
        self,
        message: str = "Resource already exists",
        detail: Optional[str] = None,
    ):
        super().__init__(message=message, detail=detail)
        self.code = "DUPLICATE_RESOURCE"