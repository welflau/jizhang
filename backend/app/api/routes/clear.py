from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import os
import logging
from app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

class ClearResponse(BaseModel):
    """Response schema for clear operation"""
    success: bool
    deleted: int

# Load admin token from environment
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

if not ADMIN_TOKEN:
    logger.warning("ADMIN_TOKEN not set, clear endpoint will reject all requests")

@router.post("/api/clear", response_model=ClearResponse)
async def clear_records(authorization: str = Header(None)):
    """Clear all access records (requires admin token)
    
    Args:
        authorization: Bearer token in Authorization header
    
    Returns:
        ClearResponse with count of deleted records
    
    Raises:
        HTTPException: 401 if unauthorized, 500 if database operation fails
    """
    # Validate authorization
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format, expected 'Bearer <token>'")
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        logger.warning(f"Unauthorized clear attempt with token: {token[:10]}...")
        raise HTTPException(status_code=401, detail="Invalid or missing admin token")
    
    try:
        async with get_db() as db:
            # Count records before deletion
            cursor = await db.execute("SELECT COUNT(*) FROM access_logs")
            count_row = await cursor.fetchone()
            deleted_count = count_row[0] if count_row else 0
            
            # Delete all records
            await db.execute("DELETE FROM access_logs")
            await db.commit()
            
            logger.info(f"Cleared {deleted_count} access records")
            
            return ClearResponse(
                success=True,
                deleted=deleted_count
            )
    except Exception as e:
        logger.exception(f"Clear operation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Clear operation failed: {str(e)}")
