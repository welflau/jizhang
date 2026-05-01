"""Health check endpoints."""
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    environment: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint.
    
    Returns:
        HealthResponse: Application health status
    """
    logger.debug("Health check requested")
    return HealthResponse(
        status="healthy",
        environment=settings.ENVIRONMENT,
        version=settings.VERSION
    )
