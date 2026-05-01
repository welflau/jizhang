from typing import Optional


class BusinessException(Exception):
    """业务异常基类"""

    def __init__(
        self,
        message: str = "Business error occurred",
        code: int = 400,
        data: Optional[dict] = None,
    ):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(self.message)


class NotFoundError(BusinessException):
    """资源未找到异常"""

    def __init__(self, message: str = "Resource not found", data: Optional[dict] = None):
        super().__init__(message=message, code=404, data=data)


class ValidationError(BusinessException):
    """数据验证异常"""

    def __init__(self, message: str = "Validation failed", data: Optional[dict] = None):
        super().__init__(message=message, code=422, data=data)


class UnauthorizedError(BusinessException):
    """未授权异常"""

    def __init__(self, message: str = "Unauthorized access", data: Optional[dict] = None):
        super().__init__(message=message, code=401, data=data)


class ForbiddenError(BusinessException):
    """禁止访问异常"""

    def __init__(self, message: str = "Access forbidden", data: Optional[dict] = None):
        super().__init__(message=message, code=403, data=data)


class ConflictError(BusinessException):
    """资源冲突异常"""

    def __init__(self, message: str = "Resource conflict", data: Optional[dict] = None):
        super().__init__(message=message, code=409, data=data)


class BadRequestError(BusinessException):
    """错误请求异常"""

    def __init__(self, message: str = "Bad request", data: Optional[dict] = None):
        super().__init__(message=message, code=400, data=data)


class InternalServerError(BusinessException):
    """服务器内部错误异常"""

    def __init__(
        self, message: str = "Internal server error", data: Optional[dict] = None
    ):
        super().__init__(message=message, code=500, data=data)


class ServiceUnavailableError(BusinessException):
    """服务不可用异常"""

    def __init__(self, message: str = "Service unavailable", data: Optional[dict] = None):
        super().__init__(message=message, code=503, data=data)


class TooManyRequestsError(BusinessException):
    """请求过多异常"""

    def __init__(self, message: str = "Too many requests", data: Optional[dict] = None):
        super().__init__(message=message, code=429, data=data)