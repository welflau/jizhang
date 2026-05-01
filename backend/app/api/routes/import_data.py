from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field, ValidationError
from typing import List
import json
import logging
from datetime import datetime
from app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

class AccessLogRecord(BaseModel):
    """Schema for validating imported access log records"""
    id: int = Field(gt=0)
    timestamp: str
    ip: str = Field(min_length=7, max_length=45)
    user_agent: str | None = None
    path: str | None = None

class ImportResponse(BaseModel):
    """Response schema for import operation"""
    success: bool
    imported_count: int
    skipped_count: int
    errors: List[str]

@router.post("/api/import", response_model=ImportResponse)
async def import_records(file: UploadFile = File(...)):
    """Import access records from JSON file
    
    Args:
        file: Uploaded JSON file containing array of access log records
    
    Returns:
        ImportResponse with counts and any errors encountered
    
    Raises:
        HTTPException: 400 if file format invalid, 500 if database operation fails
    """
    imported_count = 0
    skipped_count = 0
    errors = []
    
    try:
        # Read and parse JSON file
        content = await file.read()
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        
        if not isinstance(data, list):
            raise HTTPException(status_code=400, detail="JSON must be an array of records")
        
        # Validate records
        validated_records = []
        for idx, item in enumerate(data):
            try:
                record = AccessLogRecord(**item)
                validated_records.append(record)
            except ValidationError as e:
                errors.append(f"Record {idx}: {str(e)}")
                skipped_count += 1
        
        # Import with transaction
        async with get_db() as db:
            try:
                for record in validated_records:
                    # Check if ID already exists
                    cursor = await db.execute(
                        "SELECT id FROM access_logs WHERE id = ?",
                        (record.id,)
                    )
                    existing = await cursor.fetchone()
                    
                    if existing:
                        errors.append(f"Record ID {record.id} already exists, skipped")
                        skipped_count += 1
                        continue
                    
                    # Validate timestamp format
                    try:
                        datetime.fromisoformat(record.timestamp.replace('Z', '+00:00'))
                    except ValueError:
                        errors.append(f"Record ID {record.id}: invalid timestamp format")
                        skipped_count += 1
                        continue
                    
                    # Insert record
                    await db.execute(
                        """
                        INSERT INTO access_logs (id, timestamp, ip, user_agent, path)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (record.id, record.timestamp, record.ip, record.user_agent, record.path)
                    )
                    imported_count += 1
                
                await db.commit()
                logger.info(f"Import completed: {imported_count} imported, {skipped_count} skipped")
                
            except Exception as e:
                await db.rollback()
                logger.exception(f"Import transaction failed: {e}")
                raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
        
        return ImportResponse(
            success=True,
            imported_count=imported_count,
            skipped_count=skipped_count,
            errors=errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Import operation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Import operation failed: {str(e)}")
