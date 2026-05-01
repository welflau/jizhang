from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.schemas.response import ResponseModel
from app.core.exceptions import BusinessException
import logging
import traceback

logger = logging.getLogger(__name__)


async def exception_handler_middleware(request: Request, call_next):
    """全局异常处理中间件"""
    try:
        response = await call_next(request)
        return response
    except BusinessException as e:
        logger.warning(f"Business exception: {e.message}", extra={
            "code": e.code,
            "path": request.url.path,
            "method": request.method
        })
        return JSONResponse(
            status_code=e.status_code,
            content=ResponseModel.error(code=e.code, message=e.message).dict()
        )
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        })
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseModel.error(
                code=500,
                message="Internal server error"
            ).dict()
        )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP 异常处理器"""
    logger.warning(f"HTTP exception: {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": request.url.path,
        "method": request.method
    })
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseModel.error(
            code=exc.status_code,
            message=exc.detail
        ).dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理器"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    error_message = "; ".join(errors)
    logger.warning(f"Validation error: {error_message}", extra={
        "path": request.url.path,
        "method": request.method,
        "errors": exc.errors()
    })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseModel.error(
            code=422,
            message=f"Validation error: {error_message}"
        ).dict()
    )


def register_exception_handlers(app):
    """注册所有异常处理器"""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)