from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.schemas.user import UpdateUserInfoRequest, UserResponse
from backend.services.user_service import UserService
from backend.middleware.auth import get_current_user
from backend.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])

@router.put("/me", response_model=UserResponse)
async def update_user_info(
    update_data: UpdateUserInfoRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user information
    
    Supports updating:
    - nickname: User display name
    - avatar_url: Profile picture URL
    - password: Requires current_password for verification
    - preferences: JSON object for user settings
    
    Args:
        update_data: Update request containing fields to modify
        current_user: Current authenticated user (from JWT token)
        db: Database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException 400: Validation error or incorrect current password
        HTTPException 401: Not authenticated
        HTTPException 404: User not found
    """
    try:
        updated_user = await UserService.update_user_info(
            db,
            current_user.id,
            update_data
        )
        return UserResponse(**updated_user.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to update user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="internal error")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information
    
    Args:
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        Current user information
    """
    return UserResponse(**current_user.to_dict())