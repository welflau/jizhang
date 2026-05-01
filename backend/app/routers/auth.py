from fastapi import APIRouter, HTTPException, Depends, status
from datetime import timedelta
import aiosqlite
from typing import Optional

from ..models.user import UserCreate, UserResponse, LoginRequest, TokenResponse
from ..utils.password import hash_password, verify_password
from ..utils.jwt_handler import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..database import get_db


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Register a new user with email/phone and password.
    
    Args:
        user_data: User registration data (email/phone + password)
        db: Database connection
        
    Returns:
        Created user data (without password)
        
    Raises:
        HTTPException 400: If email/phone already exists
        HTTPException 422: If validation fails
    """
    # Check if user already exists
    if user_data.email:
        cursor = await db.execute(
            "SELECT id FROM users WHERE email = ?",
            (user_data.email,)
        )
        if await cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="email already registered"
            )
    
    if user_data.phone:
        cursor = await db.execute(
            "SELECT id FROM users WHERE phone = ?",
            (user_data.phone,)
        )
        if await cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="phone number already registered"
            )
    
    # Hash password and insert user
    hashed_pwd = hash_password(user_data.password)
    cursor = await db.execute(
        """
        INSERT INTO users (email, phone, hashed_password)
        VALUES (?, ?, ?)
        """,
        (user_data.email, user_data.phone, hashed_pwd)
    )
    await db.commit()
    
    user_id = cursor.lastrowid
    
    # Fetch created user
    cursor = await db.execute(
        "SELECT id, email, phone, created_at, is_active FROM users WHERE id = ?",
        (user_id,)
    )
    row = await cursor.fetchone()
    
    return UserResponse(
        id=row["id"],
        email=row["email"],
        phone=row["phone"],
        created_at=row["created_at"],
        is_active=bool(row["is_active"])
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Authenticate user and return JWT token.
    
    Args:
        credentials: Login credentials (email/phone + password)
        db: Database connection
        
    Returns:
        JWT access token with expiration info
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Try to find user by email or phone
    cursor = await db.execute(
        """
        SELECT id, email, phone, hashed_password, is_active
        FROM users
        WHERE email = ? OR phone = ?
        """,
        (credentials.identifier, credentials.identifier)
    )
    user = await cursor.fetchone()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="account is inactive"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user["id"]), "email": user["email"], "phone": user["phone"]}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
async def logout():
    """Logout endpoint (client should discard token).
    
    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token from storage. This endpoint exists for
    API consistency and future token blacklist implementation.
    """
    return {"message": "logged out successfully"}
