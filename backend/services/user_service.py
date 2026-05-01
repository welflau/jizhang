from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.user import User
from backend.schemas.user import UpdateUserInfoRequest
from fastapi import HTTPException
import bcrypt
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service layer for user operations"""

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
        """Get user by ID
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User object
            
        Raises:
            HTTPException: If user not found
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail=f"user {user_id} not found")
        return user

    @staticmethod
    async def update_nickname(db: AsyncSession, user: User, nickname: str) -> None:
        """Update user nickname
        
        Args:
            db: Database session
            user: User object
            nickname: New nickname
        """
        user.nickname = nickname.strip()
        logger.info(f"Updated nickname for user {user.id} to '{nickname}'")

    @staticmethod
    async def update_avatar(db: AsyncSession, user: User, avatar_url: str) -> None:
        """Update user avatar URL
        
        Args:
            db: Database session
            user: User object
            avatar_url: New avatar URL
        """
        user.avatar_url = avatar_url.strip()
        logger.info(f"Updated avatar for user {user.id} to '{avatar_url}'")

    @staticmethod
    async def update_password(
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str
    ) -> None:
        """Update user password with verification
        
        Args:
            db: Database session
            user: User object
            current_password: Current password for verification
            new_password: New password to set
            
        Raises:
            HTTPException: If current password is incorrect
        """
        # Verify current password
        if not bcrypt.checkpw(
            current_password.encode("utf-8"),
            user.password_hash.encode("utf-8")
        ):
            raise HTTPException(status_code=400, detail="current password is incorrect")
        
        # Hash new password
        salt = bcrypt.gensalt()
        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), salt)
        user.password_hash = new_hash.decode("utf-8")
        logger.info(f"Updated password for user {user.id}")

    @staticmethod
    async def update_preferences(db: AsyncSession, user: User, preferences: dict) -> None:
        """Update user preferences
        
        Args:
            db: Database session
            user: User object
            preferences: New preferences dict
        """
        # Merge with existing preferences
        current_prefs = user.get_preferences()
        current_prefs.update(preferences)
        user.set_preferences(current_prefs)
        logger.info(f"Updated preferences for user {user.id}: {list(preferences.keys())}")

    @staticmethod
    async def update_user_info(
        db: AsyncSession,
        user_id: int,
        update_data: UpdateUserInfoRequest
    ) -> User:
        """Update user information with validation
        
        Args:
            db: Database session
            user_id: User ID
            update_data: Update request data
            
        Returns:
            Updated user object
            
        Raises:
            HTTPException: If validation fails or user not found
        """
        user = await UserService.get_user_by_id(db, user_id)
        
        # Update nickname
        if update_data.nickname is not None:
            await UserService.update_nickname(db, user, update_data.nickname)
        
        # Update avatar
        if update_data.avatar_url is not None:
            await UserService.update_avatar(db, user, update_data.avatar_url)
        
        # Update password (requires current password verification)
        if update_data.new_password is not None:
            if not update_data.current_password:
                raise HTTPException(
                    status_code=400,
                    detail="current_password is required when changing password"
                )
            await UserService.update_password(
                db,
                user,
                update_data.current_password,
                update_data.new_password
            )
        
        # Update preferences
        if update_data.preferences is not None:
            await UserService.update_preferences(db, user, update_data.preferences)
        
        # Commit changes
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Successfully updated user {user_id} information")
        return user