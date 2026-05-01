from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": None
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: int
    message: str
    detail: Optional[Any] = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": 400,
                "message": "Bad Request",
                "detail": "Invalid input data"
            }
        }


def success_response(data: Any = None, message: str = "success", code: int = 200) -> dict:
    """成功响应封装"""
    return {
        "code": code,
        "message": message,
        "data": data
    }


def error_response(message: str, code: int = 400, detail: Any = None) -> dict:
    """错误响应封装"""
    response = {
        "code": code,
        "message": message
    }
    if detail is not None:
        response["detail"] = detail
    return response


class BusinessException(Exception):
    """业务异常基类"""
    def __init__(self, message: str, code: int = 400, detail: Any = None):
        self.message = message
        self.code = code
        self.detail = detail
        super().__init__(self.message)


class NotFoundError(BusinessException):
    """资源未找到异常"""
    def __init__(self, message: str = "Resource not found", detail: Any = None):
        super().__init__(message=message, code=404, detail=detail)


class ValidationError(BusinessException):
    """数据验证异常"""
    def __init__(self, message: str = "Validation error", detail: Any = None):
        super().__init__(message=message, code=422, detail=detail)


class AuthenticationError(BusinessException):
    """认证异常"""
    def __init__(self, message: str = "Authentication failed", detail: Any = None):
        super().__init__(message=message, code=401, detail=detail)


class AuthorizationError(BusinessException):
    """授权异常"""
    def __init__(self, message: str = "Permission denied", detail: Any = None):
        super().__init__(message=message, code=403, detail=detail)


class ConflictError(BusinessException):
    """资源冲突异常"""
    def __init__(self, message: str = "Resource conflict", detail: Any = None):
        super().__init__(message=message, code=409, detail=detail)


class BadRequestError(BusinessException):
    """错误请求异常"""
    def __init__(self, message: str = "Bad request", detail: Any = None):
        super().__init__(message=message, code=400, detail=detail)


class InternalServerError(BusinessException):
    """服务器内部错误"""
    def __init__(self, message: str = "Internal server error", detail: Any = None):
        super().__init__(message=message, code=500, detail=detail)