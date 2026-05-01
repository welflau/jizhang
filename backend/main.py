from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from backend.routers import bills
from backend.database.connection import init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bill Management API",
    description="API for managing personal bills with advanced query capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bills.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting up application...")
    await init_database()
    logger.info("Application startup complete")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Bill Management API is running"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
