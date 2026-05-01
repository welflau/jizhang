"""
FastAPI Application Initialization Module

This module initializes the FastAPI application with core configurations including:
- CORS middleware
- Logging system
- Environment variables
- Application metadata
"""

import logging
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment
ENV = os.getenv("ENV", "development")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DIR = Path("logs")

# Create logs directory if it doesn't exist
if not LOG_DIR.exists():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging handlers based on environment
handlers = []

# Console handler (always enabled)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
handlers.append(console_handler)

# File handler (enabled in production or when specified)
if ENV == "production" or os.getenv("LOG_TO_FILE", "False").lower() == "true":
    file_handler = logging.FileHandler(
        LOG_DIR / f"app_{ENV}.log",
        encoding="utf-8"
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handlers.append(file_handler)

# Configure root logger
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=handlers
)

logger = logging.getLogger(__name__)

# Log startup information
logger.info(f"Starting application in {ENV} environment")
logger.info(f"Debug mode: {DEBUG}")
logger.info(f"Log level: {LOG_LEVEL}")

# Initialize FastAPI application
app = FastAPI(
    title=os.getenv("APP_NAME", "FastAPI Application"),
    description=os.getenv("APP_DESCRIPTION", "FastAPI application with structured architecture"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    debug=DEBUG,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
)

# Configure CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
ALLOWED_METHODS = os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,PATCH,OPTIONS").split(",")
ALLOWED_HEADERS = os.getenv("ALLOWED_HEADERS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=os.getenv("ALLOW_CREDENTIALS", "True").lower() == "true",
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    expose_headers=os.getenv("EXPOSE_HEADERS", "").split(",") if os.getenv("EXPOSE_HEADERS") else [],
    max_age=int(os.getenv("CORS_MAX_AGE", "600")),
)

logger.info(f"CORS configured with origins: {ALLOWED_ORIGINS}")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify application status
    """
    return {
        "status": "healthy",
        "environment": ENV,
        "version": os.getenv("APP_VERSION", "1.0.0")
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with basic application information
    """
    return {
        "message": "Welcome to FastAPI Application",
        "docs": "/docs" if DEBUG else "Documentation disabled in production",
        "health": "/health"
    }


# Application startup event
@app.on_event("startup")
async def startup_event():
    """
    Execute tasks on application startup
    """
    logger.info("Application startup complete")
    logger.info(f"API documentation available at: /docs")


# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute cleanup tasks on application shutdown
    """
    logger.info("Application shutting down")


# Create necessary directories
def create_project_structure():
    """
    Create project directory structure if it doesn't exist
    """
    directories = [
        "app/api",
        "app/models",
        "app/schemas",
        "app/services",
        "app/core",
        "app/utils",
    ]
    
    base_path = Path(__file__).parent.parent
    
    for directory in directories:
        dir_path = base_path / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            # Create __init__.py in each directory
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
            logger.info(f"Created directory: {directory}")


# Create project structure on module import
create_project_structure()

logger.info("FastAPI application initialized successfully")