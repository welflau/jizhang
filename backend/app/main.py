from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.routers import auth
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Unified response format helper
def unified_response(success: bool, data=None, message: str = "", code: int = 200):
    """Create unified response format."""
    return {
        "success": success,
        "data": data,
        "message": message,
        "code": code
    }


# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with unified format."""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=unified_response(
            success=False,
            data=None,
            message=str(exc.detail),
            code=exc.status_code
        )
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with unified format."""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=unified_response(
            success=False,
            data={"errors": exc.errors()},
            message="Validation error",
            code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with unified format."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=unified_response(
            success=False,
            data=None,
            message="Internal server error" if not settings.DEBUG else str(exc),
            code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    )


# Include routers
app.include_router(auth.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "app": settings.APP_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )