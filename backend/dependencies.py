"""FastAPI dependency injection utilities."""

import aiosqlite
import os
from typing import AsyncGenerator
from fastapi import Header, HTTPException, status

DB_PATH = os.getenv("DB_PATH", "backend/app.db")


async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """
    Database connection dependency.
    
    Yields:
        Database connection with foreign keys enabled
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        db.row_factory = aiosqlite.Row
        yield db


async def get_current_user(authorization: str = Header(None)) -> int:
    """
    Extract and validate user ID from authorization header.
    
    Args:
        authorization: Authorization header value (format: "Bearer <user_id>")
        
    Returns:
        User ID
        
    Raises:
        HTTPException: 401 if authorization header is missing or invalid
        
    Note:
        This is a simplified auth implementation for development.
        Production should use JWT tokens or OAuth2.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
        user_id = int(token)
        return user_id
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <user_id>"
        )
