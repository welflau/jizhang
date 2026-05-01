"""FastAPI application entry point.

Main application setup with database initialization and route registration.
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.
    
    Runs database initialization on startup.
    """
    logger.info("Starting application...")
    try:
        await init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.exception(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    logger.info("Shutting down application...")


app = FastAPI(
    title="Personal Finance Manager",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Personal Finance Manager API"}


@app.get("/health")
async def health_check():
    """Detailed health check with database status."""
    from database import get_db_connection, get_current_version
    
    try:
        async with await get_db_connection() as conn:
            version = await get_current_version(conn)
        return {
            "status": "healthy",
            "database": "connected",
            "schema_version": version
        }
    except Exception as e:
        logger.exception("Health check failed")
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV") == "development"
    )
