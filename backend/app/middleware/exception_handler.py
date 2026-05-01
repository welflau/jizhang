from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
import logging
import traceback
from typing import Union

logger = logging.getLogger(__name__)


class BaseAPIException(Exception):
    """基础API异常类"""
    def __init__(self, message: str = "Internal Server Error", code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundError(BaseAPIException):
    """资源未找到异常"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, code=404)


class ValidationError(BaseAPIException):
    """数据验证异常"""
    def __init__(self, message: str = "Validation error"):
        super().__init__(message=message, code=400)


class UnauthorizedError(BaseAPIException):
    """未授权异常"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, code=401)


class ForbiddenError(BaseAPIException):
    """禁止访问异常"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, code=403)


class ConflictError(BaseAPIException):
    """资源冲突异常"""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message=message, code=409)


class BadRequestError(BaseAPIException):
    """错误请求异常"""
    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, code=400)


class InternalServerError(BaseAPIException):
    """内部服务器错误"""
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message=message, code=500)


async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    """处理自定义API异常"""
    logger.warning(f"API Exception: {exc.code} - {exc.message} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": None
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """处理HTTP异常"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证异常"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    error_message = "; ".join(errors) if errors else "Validation error"
    logger.warning(f"Validation Error: {error_message} - Path: {request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": f"Validation error: {error_message}",
            "data": {"errors": exc.errors()}
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """处理SQLAlchemy数据库异常"""
    logger.error(f"Database Error: {str(exc)} - Path: {request.url.path}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "Database error occurred",
            "data": None
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(f"Unhandled Exception: {str(exc)} - Path: {request.url.path}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "Internal server error",
            "data": None
        }
    )


def register_exception_handlers(app):
    """注册所有异常处理器"""
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)