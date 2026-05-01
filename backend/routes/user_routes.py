from fastapi import APIRouter, Depends, HTTPException, status
from backend.models.user import UserUpdateRequest, UserResponse
from backend.services.user_service import UserService
from backend.middleware.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/user", tags=["user"])
user_service = UserService()

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile
    
    Args:
        current_user: Authenticated user from JWT token
        
    Returns:
        User profile data
        
    Raises:
        HTTPException: 404 if user not found
    """
    user_id = current_user["user_id"]
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    return user

@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    request: UserUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile
    
    Args:
        request: User update request with optional fields
        current_user: Authenticated user from JWT token
        
    Returns:
        Updated user profile data
        
    Raises:
        HTTPException: 400 if validation fails, 401 if password incorrect, 404 if user not found
    """
    user_id = current_user["user_id"]
    
    # If changing password, verify current password first
    if request.new_password:
        if not request.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="current_password is required when changing password"
            )
        
        password_valid = await user_service.verify_password(user_id, request.current_password)
        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
    
    # Convert preferences model to dict if provided
    preferences_dict = None
    if request.preferences:
        preferences_dict = request.preferences.dict()
    
    # Update user profile
    try:
        updated_user = await user_service.update_user(
            user_id=user_id,
            nickname=request.nickname,
            avatar=request.avatar,
            new_password=request.new_password,
            preferences=preferences_dict
        )
        
        logger.info(f"User {user_id} profile updated via API")
        return updated_user
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error updating profile for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )