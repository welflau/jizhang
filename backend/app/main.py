from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.routers import auth, backup, categories
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


# Exception handler middleware
@app.middleware("http")
async def exception_handler_middleware(request: Request, call_next):
    """Catch all exceptions and return unified response format."""
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal server error",
                "data": None
            }
        )


# Include routers
app.include_router(auth.router)
app.include_router(backup.router)
app.include_router(categories.router)


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