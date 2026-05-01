import logging
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import (
    BaseAPIException,
    NotFoundError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    InternalServerError
)
from app.schemas.response import ResponseModel

logger = logging.getLogger(__name__)


async def exception_handler_middleware(request: Request, call_next):
    """
    全局异常处理中间件
    捕获所有未处理的异常并返回统一格式
    """
    try:
        response = await call_next(request)
        return response
    except BaseAPIException as exc:
        # 业务异常
        logger.warning(
            f"Business exception: {exc.message}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "code": exc.code
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ResponseModel.error(
                code=exc.code,
                message=exc.message,
                data=exc.data
            ).dict()
        )
    except Exception as exc:
        # 未预期的系统异常
        logger.error(
            f"Unexpected exception: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method
            },
            exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseModel.error(
                code=500,
                message="Internal server error",
                data={"detail": str(exc)}
            ).dict()
        )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    处理 Starlette HTTP 异常
    """
    logger.warning(
        f"HTTP exception: {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseModel.error(
            code=exc.status_code,
            message=exc.detail or "HTTP error",
            data=None
        ).dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理请求验证异常
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append({
            "field": field,
            "message": message,
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error: {errors}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseModel.error(
            code=422,
            message="Validation error",
            data={"errors": errors}
        ).dict()
    )


async def base_api_exception_handler(request: Request, exc: BaseAPIException):
    """
    处理自定义业务异常
    """
    logger.warning(
        f"API exception: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "code": exc.code
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseModel.error(
            code=exc.code,
            message=exc.message,
            data=exc.data
        ).dict()
    )


def register_exception_handlers(app):
    """
    注册所有异常处理器到 FastAPI 应用
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    app.add_exception_handler(NotFoundError, base_api_exception_handler)
    app.add_exception_handler(ValidationError, base_api_exception_handler)
    app.add_exception_handler(UnauthorizedError, base_api_exception_handler)
    app.add_exception_handler(ForbiddenError, base_api_exception_handler)
    app.add_exception_handler(InternalServerError, base_api_exception_handler)