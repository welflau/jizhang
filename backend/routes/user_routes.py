from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import jwt
import os
import logging

from models.user import UpdateUserRequest, UpdateUserResponse, UserResponse
from services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/user", tags=["user"])
security = HTTPBearer()

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Extract and verify user ID from JWT token
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        User ID from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user_id not found"
            )
        return int(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id)
):
    """Get current user information
    
    Returns:
        Current user data
    """
    service = UserService()
    user = await service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user)

@router.put("/update", response_model=UpdateUserResponse)
async def update_user_info(
    request: UpdateUserRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Update user information
    
    Supports updating:
    - nickname: User display name
    - avatar: Avatar URL or base64 data
    - password: Requires old_password verification
    - preferences: User preference settings
    
    Args:
        request: Update request with fields to modify
        user_id: Current user ID from JWT token
        
    Returns:
        Updated user information
    """
    service = UserService()
    
    try:
        updated_user = await service.update_user_info(
            user_id=user_id,
            nickname=request.nickname,
            avatar=request.avatar,
            old_password=request.old_password,
            new_password=request.new_password,
            preferences=request.preferences.dict() if request.preferences else None
        )
        
        return UpdateUserResponse(
            success=True,
            message="User information updated successfully",
            user=UserResponse(**updated_user)
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions from service layer
        raise
    except Exception as e:
        logger.exception(f"Unexpected error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user information"
        )

@router.patch("/preferences", response_model=UpdateUserResponse)
async def update_preferences(
    preferences: Dict[str, Any],
    user_id: int = Depends(get_current_user_id)
):
    """Update user preferences (merge with existing)
    
    Args:
        preferences: Preference key-value pairs to update
        user_id: Current user ID from JWT token
        
    Returns:
        Updated user information
    """
    service = UserService()
    
    try:
        updated_user = await service.update_preferences(
            user_id=user_id,
            preferences=preferences
        )
        
        return UpdateUserResponse(
            success=True,
            message="User preferences updated successfully",
            user=UserResponse(**updated_user)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error updating preferences for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )