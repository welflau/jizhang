from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
import logging
import traceback
from typing import Union

from app.schemas.response import ResponseModel
from app.core.exceptions import (
    BusinessException,
    NotFoundException,
    ValidationException,
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
)

logger = logging.getLogger(__name__)


async def exception_handler_middleware(request: Request, call_next):
    """
    全局异常处理中间件
    捕获所有未处理的异常并返回统一格式
    """
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(
            f"Unhandled exception: {str(exc)}\n"
            f"Path: {request.url.path}\n"
            f"Method: {request.method}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseModel.error(
                message="Internal server error",
                code=500
            ).dict()
        )


async def business_exception_handler(request: Request, exc: BusinessException):
    """
    业务异常处理器
    """
    logger.warning(
        f"Business exception: {exc.message}\n"
        f"Path: {request.url.path}\n"
        f"Code: {exc.code}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseModel.error(
            message=exc.message,
            code=exc.code
        ).dict()
    )


async def not_found_exception_handler(request: Request, exc: NotFoundException):
    """
    资源不存在异常处理器
    """
    logger.info(
        f"Not found: {exc.message}\n"
        f"Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ResponseModel.error(
            message=exc.message,
            code=exc.code
        ).dict()
    )


async def validation_exception_handler(request: Request, exc: ValidationException):
    """
    验证异常处理器
    """
    logger.info(
        f"Validation error: {exc.message}\n"
        f"Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ResponseModel.error(
            message=exc.message,
            code=exc.code
        ).dict()
    )


async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    """
    未授权异常处理器
    """
    logger.warning(
        f"Unauthorized access: {exc.message}\n"
        f"Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=ResponseModel.error(
            message=exc.message,
            code=exc.code
        ).dict(),
        headers={"WWW-Authenticate": "Bearer"}
    )


async def forbidden_exception_handler(request: Request, exc: ForbiddenException):
    """
    禁止访问异常处理器
    """
    logger.warning(
        f"Forbidden access: {exc.message}\n"
        f"Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=ResponseModel.error(
            message=exc.message,
            code=exc.code
        ).dict()
    )


async def conflict_exception_handler(request: Request, exc: ConflictException):
    """
    冲突异常处理器
    """
    logger.info(
        f"Conflict: {exc.message}\n"
        f"Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=ResponseModel.error(
            message=exc.message,
            code=exc.code
        ).dict()
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    HTTP异常处理器
    """
    logger.info(
        f"HTTP exception: {exc.detail}\n"
        f"Path: {request.url.path}\n"
        f"Status: {exc.status_code}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseModel.error(
            message=exc.detail,
            code=exc.status_code
        ).dict()
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    请求验证异常处理器
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        message = error["msg"]
        errors.append(f"{field}: {message}" if field else message)
    
    error_message = "; ".join(errors)
    logger.info(
        f"Request validation error: {error_message}\n"
        f"Path: {request.url.path}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseModel.error(
            message=f"Validation error: {error_message}",
            code=422,
            data={"errors": exc.errors()}
        ).dict()
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    数据库异常处理器
    """
    logger.error(
        f"Database error: {str(exc)}\n"
        f"Path: {request.url.path}\n"
        f"Traceback: {traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ResponseModel.error(
            message="Database error occurred",
            code=500
        ).dict()
    )


def register_exception_handlers(app):
    """
    注册所有异常处理器到FastAPI应用
    """
    # 业务异常
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(NotFoundException, not_found_exception_handler)
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(UnauthorizedException, unauthorized_exception_handler)
    app.add_exception_handler(ForbiddenException, forbidden_exception_handler)
    app.add_exception_handler(ConflictException, conflict_exception_handler)
    
    # 框架异常
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    
    # 数据库异常
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    logger.info("Exception handlers registered successfully")