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
    def __init__(
        self,
        message: str = "操作失败",
        code: int = 400,
        data: Union[dict, list, None] = None
    ):
        self.message = message
        self.code = code
        self.data = data
        super().__init__(self.message)


class NotFoundError(BaseAPIException):
    """资源未找到异常"""
    def __init__(self, message: str = "资源未找到", data: Union[dict, list, None] = None):
        super().__init__(message=message, code=404, data=data)


class ValidationError(BaseAPIException):
    """数据验证异常"""
    def __init__(self, message: str = "数据验证失败", data: Union[dict, list, None] = None):
        super().__init__(message=message, code=422, data=data)


class UnauthorizedError(BaseAPIException):
    """未授权异常"""
    def __init__(self, message: str = "未授权访问", data: Union[dict, list, None] = None):
        super().__init__(message=message, code=401, data=data)


class ForbiddenError(BaseAPIException):
    """禁止访问异常"""
    def __init__(self, message: str = "禁止访问", data: Union[dict, list, None] = None):
        super().__init__(message=message, code=403, data=data)


class ConflictError(BaseAPIException):
    """资源冲突异常"""
    def __init__(self, message: str = "资源冲突", data: Union[dict, list, None] = None):
        super().__init__(message=message, code=409, data=data)


class BadRequestError(BaseAPIException):
    """错误请求异常"""
    def __init__(self, message: str = "错误的请求", data: Union[dict, list, None] = None):
        super().__init__(message=message, code=400, data=data)


class InternalServerError(BaseAPIException):
    """服务器内部错误"""
    def __init__(self, message: str = "服务器内部错误", data: Union[dict, list, None] = None):
        super().__init__(message=message, code=500, data=data)


async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    """处理自定义API异常"""
    logger.warning(
        f"API Exception: {exc.message} | Path: {request.url.path} | Code: {exc.code}"
    )
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "message": exc.message,
            "data": exc.data
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """处理HTTP异常"""
    logger.warning(
        f"HTTP Exception: {exc.detail} | Path: {request.url.path} | Status: {exc.status_code}"
    )
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
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation Error: {errors} | Path: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "请求参数验证失败",
            "data": {"errors": errors}
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """处理SQLAlchemy数据库异常"""
    logger.error(
        f"Database Error: {str(exc)} | Path: {request.url.path}\n{traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "数据库操作失败",
            "data": None
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(
        f"Unhandled Exception: {str(exc)} | Path: {request.url.path}\n{traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
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