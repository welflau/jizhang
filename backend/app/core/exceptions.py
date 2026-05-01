from typing import Any, Optional


class AppException(Exception):
    """Base application exception"""
    
    def __init__(
        self,
        message: str = "Application error",
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
    
    def __init__(self, message: str = "Validation error", data: Optional[Any] = None):
        super().__init__(message=message, code=422, data=data)


class AuthenticationError(AppException):
    """Authentication error exception"""
    
    def __init__(self, message: str = "Authentication failed", data: Optional[Any] = None):
        super().__init__(message=message, code=401, data=data)


class AuthorizationError(AppException):
    """Authorization error exception"""
    
    def __init__(self, message: str = "Permission denied", data: Optional[Any] = None):
        super().__init__(message=message, code=403, data=data)


class BadRequestError(AppException):
    """Bad request exception"""
    
    def __init__(self, message: str = "Bad request", data: Optional[Any] = None):
        super().__init__(message=message, code=400, data=data)


class ConflictError(AppException):
    """Conflict error exception"""
    
    def __init__(self, message: str = "Resource conflict", data: Optional[Any] = None):
        super().__init__(message=message, code=409, data=data)


class InternalServerError(AppException):
    """Internal server error exception"""
    
    def __init__(self, message: str = "Internal server error", data: Optional[Any] = None):
        super().__init__(message=message, code=500, data=data)


class DatabaseError(AppException):
    """Database error exception"""
    
    def __init__(self, message: str = "Database error", data: Optional[Any] = None):
        super().__init__(message=message, code=500, data=data)


class ExternalServiceError(AppException):
    """External service error exception"""
    
    def __init__(self, message: str = "External service error", data: Optional[Any] = None):
        super().__init__(message=message, code=502, data=data)


class RateLimitError(AppException):
    """Rate limit exceeded exception"""
    
    def __init__(self, message: str = "Rate limit exceeded", data: Optional[Any] = None):
        super().__init__(message=message, code=429, data=data)


class ServiceUnavailableError(AppException):
    """Service unavailable exception"""
    
    def __init__(self, message: str = "Service unavailable", data: Optional[Any] = None):
        super().__init__(message=message, code=503, data=data)