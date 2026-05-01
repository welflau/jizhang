"""
API Router Initialization Module

This module initializes and configures all API routers for the FastAPI application.
It serves as the central point for registering all API endpoints.
"""

from fastapi import APIRouter

# Create main API router
api_router = APIRouter()

# TODO: Import and include specific routers when they are created
# Example:
# from app.api.endpoints import users, items, auth
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])
# api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])


@api_router.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        dict: Status message indicating API is operational
    """
    return {
        "status": "healthy",
        "message": "API is running successfully"
    }


@api_router.get("/", tags=["root"])
async def root():
    """
    Root endpoint providing basic API information.
    
    Returns:
        dict: Welcome message and API version
    """
    return {
        "message": "Welcome to FastAPI Application",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }