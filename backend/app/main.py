from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import init_db, close_db
from backend.app.core.middleware import JWTAuthMiddleware
from backend.app.routers import auth, budgets
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

# JWT authentication middleware
app.add_middleware(JWTAuthMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(budgets.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection pool on application shutdown."""
    logger.info("Closing database connection pool...")
    await close_db()
    logger.info("Database connection pool closed successfully")


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