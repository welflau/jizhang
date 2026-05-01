from typing import Any, Optional


class AppException(Exception):
    """Base application exception"""
    
    def __init__(
        self,
        message: str = "An error occurred",
        code: int = 500,
        data: Optional[Any] = None
    ):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(self.message)


class NotFoundError(AppException):
    """Resource not found exception"""
    
    def __init__(self, message: str = "Resource not found", data: Optional[Any] = None):
        super().__init__(message=message, code=404, data=data)


class ValidationError(AppException):
    """Validation error exception"""
    
    def __init__(self, message: str = "Validation failed", data: Optional[Any] = None):
        super().__init__(message=message, code=400, data=data)


class UnauthorizedError(AppException):
    """Unauthorized access exception"""
    
    def __init__(self, message: str = "Unauthorized access", data: Optional[Any] = None):
        super().__init__(message=message, code=401, data=data)


class ForbiddenError(AppException):
    """Forbidden access exception"""
    
    def __init__(self, message: str = "Forbidden access", data: Optional[Any] = None):
        super().__init__(message=message, code=403, data=data)


class ConflictError(AppException):
    """Conflict exception (e.g., duplicate resource)"""
    
    def __init__(self, message: str = "Resource conflict", data: Optional[Any] = None):
        super().__init__(message=message, code=409, data=data)


class BadRequestError(AppException):
    """Bad request exception"""
    
    def __init__(self, message: str = "Bad request", data: Optional[Any] = None):
        super().__init__(message=message, code=400, data=data)


class InternalServerError(AppException):
    """Internal server error exception"""
    
    def __init__(self, message: str = "Internal server error", data: Optional[Any] = None):
        super().__init__(message=message, code=500, data=data)


class ServiceUnavailableError(AppException):
    """Service unavailable exception"""
    
    def __init__(self, message: str = "Service unavailable", data: Optional[Any] = None):
        super().__init__(message=message, code=503, data=data)


class DatabaseError(AppException):
    """Database operation error exception"""
    
    def __init__(self, message: str = "Database operation failed", data: Optional[Any] = None):
        super().__init__(message=message, code=500, data=data)


class AuthenticationError(AppException):
    """Authentication error exception"""
    
    def __init__(self, message: str = "Authentication failed", data: Optional[Any] = None):
        super().__init__(message=message, code=401, data=data)


class TokenExpiredError(AppException):
    """Token expired exception"""
    
    def __init__(self, message: str = "Token has expired", data: Optional[Any] = None):
        super().__init__(message=message, code=401, data=data)


class InvalidTokenError(AppException):
    """Invalid token exception"""
    
    def __init__(self, message: str = "Invalid token", data: Optional[Any] = None):
        super().__init__(message=message, code=401, data=data)


class PermissionDeniedError(AppException):
    """Permission denied exception"""
    
    def __init__(self, message: str = "Permission denied", data: Optional[Any] = None):
        super().__init__(message=message, code=403, data=data)


class RateLimitError(AppException):
    """Rate limit exceeded exception"""
    
    def __init__(self, message: str = "Rate limit exceeded", data: Optional[Any] = None):
        super().__init__(message=message, code=429, data=data)


class FileUploadError(AppException):
    """File upload error exception"""
    
    def __init__(self, message: str = "File upload failed", data: Optional[Any] = None):
        super().__init__(message=message, code=400, data=data)


class ExternalServiceError(AppException):
    """External service error exception"""
    
    def __init__(self, message: str = "External service error", data: Optional[Any] = None):
        super().__init__(message=message, code=502, data=data)