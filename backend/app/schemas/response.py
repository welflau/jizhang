from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel
from fastapi import status

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


class ResponseCode:
    """响应状态码"""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    VALIDATION_ERROR = 422
    INTERNAL_ERROR = 500


def success_response(data: Any = None, message: str = "success", code: int = ResponseCode.SUCCESS) -> dict:
    """成功响应"""
    return {
        "code": code,
        "message": message,
        "data": data
    }


def error_response(message: str = "error", code: int = ResponseCode.BAD_REQUEST, data: Any = None) -> dict:
    """错误响应"""
    return {
        "code": code,
        "message": message,
        "data": data
    }


class APIException(Exception):
    """API基础异常类"""
    def __init__(
        self,
        message: str = "Internal server error",
        code: int = ResponseCode.INTERNAL_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        data: Any = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.data = data
        super().__init__(self.message)


class NotFoundError(APIException):
    """资源不存在异常"""
    def __init__(self, message: str = "Resource not found", data: Any = None):
        super().__init__(
            message=message,
            code=ResponseCode.NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            data=data
        )


class ValidationError(APIException):
    """数据验证异常"""
    def __init__(self, message: str = "Validation error", data: Any = None):
        super().__init__(
            message=message,
            code=ResponseCode.VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            data=data
        )


class UnauthorizedError(APIException):
    """未授权异常"""
    def __init__(self, message: str = "Unauthorized", data: Any = None):
        super().__init__(
            message=message,
            code=ResponseCode.UNAUTHORIZED,
            status_code=status.HTTP_401_UNAUTHORIZED,
            data=data
        )


class ForbiddenError(APIException):
    """禁止访问异常"""
    def __init__(self, message: str = "Forbidden", data: Any = None):
        super().__init__(
            message=message,
            code=ResponseCode.FORBIDDEN,
            status_code=status.HTTP_403_FORBIDDEN,
            data=data
        )


class ConflictError(APIException):
    """资源冲突异常"""
    def __init__(self, message: str = "Resource conflict", data: Any = None):
        super().__init__(
            message=message,
            code=ResponseCode.CONFLICT,
            status_code=status.HTTP_409_CONFLICT,
            data=data
        )


class BadRequestError(APIException):
    """错误请求异常"""
    def __init__(self, message: str = "Bad request", data: Any = None):
        super().__init__(
            message=message,
            code=ResponseCode.BAD_REQUEST,
            status_code=status.HTTP_400_BAD_REQUEST,
            data=data
        )


class InternalServerError(APIException):
    """服务器内部错误"""
    def __init__(self, message: str = "Internal server error", data: Any = None):
        super().__init__(
            message=message,
            code=ResponseCode.INTERNAL_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            data=data
        )