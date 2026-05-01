from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
from app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/export")
async def export_records():
    """Export all access records as JSON
    
    Returns:
        JSON array of access log records sorted by timestamp descending
    
    Raises:
        HTTPException: 500 if database query fails
    """
    try:
        async with get_db() as db:
            cursor = await db.execute("""
                SELECT id, timestamp, ip, user_agent, path 
                FROM access_logs 
                ORDER BY timestamp DESC
            """)
            rows = await cursor.fetchall()
            
            records = [
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "ip": row[2],
                    "user_agent": row[3],
                    "path": row[4]
                }
                for row in rows
            ]
            
            logger.info(f"Exported {len(records)} access records")
            
            return JSONResponse(
                content=records,
                headers={
                    "Content-Disposition": "attachment; filename=access_logs_export.json"
                }
            )
    except Exception as e:
        logger.exception(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
