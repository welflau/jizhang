"""
FastAPI Application Initialization Module

This module initializes the FastAPI application with core configurations including:
- CORS middleware
- Logging system
- Environment variables
- API routers
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get environment settings
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
APP_NAME = os.getenv('APP_NAME', 'FastAPI Application')
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# CORS settings
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
CORS_ALLOW_CREDENTIALS = os.getenv('CORS_ALLOW_CREDENTIALS', 'True').lower() == 'true'
CORS_ALLOW_METHODS = os.getenv('CORS_ALLOW_METHODS', '*').split(',')
CORS_ALLOW_HEADERS = os.getenv('CORS_ALLOW_HEADERS', '*').split(',')


def setup_logging():
    """
    Configure logging system based on environment
    - Development: Console output with DEBUG level
    - Production: File output with INFO level and rotation
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (enabled in production or when specified)
    if ENVIRONMENT == 'production' or os.getenv('LOG_TO_FILE', 'False').lower() == 'true':
        file_handler = RotatingFileHandler(
            logs_dir / f'{APP_NAME.lower().replace(" ", "_")}.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    logger.info(f"Logging initialized - Environment: {ENVIRONMENT}, Level: {LOG_LEVEL}")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application instance
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Create FastAPI app
    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        debug=DEBUG,
        docs_url='/docs' if DEBUG else None,
        redoc_url='/redoc' if DEBUG else None,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_ALLOW_CREDENTIALS,
        allow_methods=CORS_ALLOW_METHODS,
        allow_headers=CORS_ALLOW_HEADERS,
    )
    
    logger.info(f"CORS configured - Origins: {CORS_ORIGINS}")
    
    # Health check endpoint
    @app.get('/health')
    async def health_check():
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'environment': ENVIRONMENT,
            'version': APP_VERSION
        }
    
    # Root endpoint
    @app.get('/')
    async def root():
        """Root endpoint"""
        return {
            'message': f'Welcome to {APP_NAME}',
            'version': APP_VERSION,
            'docs': '/docs' if DEBUG else 'disabled'
        }
    
    logger.info(f"{APP_NAME} v{APP_VERSION} initialized successfully")
    logger.info(f"Environment: {ENVIRONMENT}, Debug: {DEBUG}")
    
    return app


# Create application instance
app = create_app()


# Import and include API routers (will be added later)
# from app.api import users, items
# app.include_router(users.router, prefix='/api/v1/users', tags=['users'])
# app.include_router(items.router, prefix='/api/v1/items', tags=['items'])