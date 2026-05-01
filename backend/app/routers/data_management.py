from fastapi import APIRouter, HTTPException, UploadFile, File, Header, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
import logging
from typing import Optional
from datetime import datetime

from ..database import get_db
from ..models import AccessLog

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/export")
async def export_data(db: Session = Depends(get_db)):
    """
    Export all access records as JSON, sorted by timestamp descending.
    
    Returns:
        JSON file with array of records containing id, timestamp, ip, user_agent, etc.
    """
    try:
        logger.info("Received export request")
        
        # Query all records ordered by timestamp descending
        records = db.query(AccessLog).order_by(AccessLog.timestamp.desc()).all()
        
        # Serialize to JSON-compatible format
        data = []
        for record in records:
            data.append({
                "id": record.id,
                "timestamp": record.timestamp.isoformat() if isinstance(record.timestamp, datetime) else record.timestamp,
                "ip": record.ip,
                "user_agent": record.user_agent,
                "path": getattr(record, 'path', '/'),
                "method": getattr(record, 'method', 'GET')
            })
        
        logger.info(f"Exported {len(data)} records")
        
        return JSONResponse(
            content=data,
            headers={
                "Content-Disposition": "attachment; filename=access_logs_export.json"
            }
        )
    
    except Exception as e:
        logger.error(f"Export error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Import access records from JSON file with transaction support.
    
    Args:
        file: JSON file containing array of records
    
    Returns:
        Statistics about imported, skipped, and error records
    """
    try:
        logger.info(f"Received import request: {file.filename}")
        
        # Read and parse JSON file
        content = await file.read()
        try:
            records = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        
        if not isinstance(records, list):
            raise HTTPException(status_code=400, detail="JSON must be an array of records")
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        # Use transaction for atomic operation
        try:
            # Get existing IDs to check for duplicates
            existing_ids = set()
            if records:
                record_ids = [r.get('id') for r in records if r.get('id')]
                if record_ids:
                    existing = db.query(AccessLog.id).filter(AccessLog.id.in_(record_ids)).all()
                    existing_ids = {row[0] for row in existing}
            
            # Process each record
            for idx, record in enumerate(records):
                try:
                    # Validate required fields
                    if not isinstance(record, dict):
                        errors.append({"index": idx, "error": "Record must be an object"})
                        continue
                    
                    record_id = record.get('id')
                    
                    # Skip if ID already exists
                    if record_id and record_id in existing_ids:
                        skipped_count += 1
                        logger.debug(f"Skipped duplicate ID: {record_id}")
                        continue
                    
                    # Parse timestamp
                    timestamp_str = record.get('timestamp')
                    if timestamp_str:
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        except ValueError:
                            timestamp = datetime.now()
                    else:
                        timestamp = datetime.now()
                    
                    # Create new record
                    new_record = AccessLog(
                        id=record_id,
                        timestamp=timestamp,
                        ip=record.get('ip', 'unknown'),
                        user_agent=record.get('user_agent', 'unknown')
                    )
                    
                    # Set optional fields if they exist in model
                    if hasattr(AccessLog, 'path'):
                        new_record.path = record.get('path', '/')
                    if hasattr(AccessLog, 'method'):
                        new_record.method = record.get('method', 'GET')
                    
                    db.add(new_record)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append({"index": idx, "error": str(e)})
                    logger.warning(f"Failed to import record {idx}: {str(e)}")
            
            # Commit transaction
            db.commit()
            logger.info(f"Import completed: {imported_count} imported, {skipped_count} skipped, {len(errors)} errors")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Transaction failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Import transaction failed: {str(e)}")
        
        return {
            "success": True,
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "errors": errors[:10]  # Limit error list to first 10
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Import error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/clear")
async def clear_data(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Clear all access records with token verification.
    
    Args:
        authorization: Bearer token from header
        token: Token from query parameter (alternative)
    
    Returns:
        Number of deleted records
    """
    try:
        logger.info("Received clear request")
        
        # Extract token from header or query parameter
        auth_token = None
        if authorization and authorization.startswith('Bearer '):
            auth_token = authorization[7:]
        elif token:
            auth_token = token
        
        # Verify token (simple validation - in production use proper auth)
        # For now, require any non-empty token
        if not auth_token or len(auth_token) < 8:
            logger.warning("Clear request rejected: invalid or missing token")
            raise HTTPException(
                status_code=401,
                detail="Valid authorization token required (min 8 characters)"
            )
        
        # Count records before deletion
        count = db.query(AccessLog).count()
        
        # Delete all records
        try:
            db.query(AccessLog).delete()
            db.commit()
            logger.info(f"Cleared {count} records")
        except Exception as e:
            db.rollback()
            logger.error(f"Clear operation failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Clear operation failed: {str(e)}")
        
        return {
            "success": True,
            "deleted_count": count
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Clear error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")
