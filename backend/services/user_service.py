import aiosqlite
import bcrypt
import json
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service layer for user operations"""
    
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User data dict or None if not found
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT id, username, nickname, avatar, email, preferences, created_at, updated_at FROM users WHERE id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    user_dict = dict(row)
                    # Parse JSON preferences
                    if user_dict.get('preferences'):
                        try:
                            user_dict['preferences'] = json.loads(user_dict['preferences'])
                        except json.JSONDecodeError:
                            user_dict['preferences'] = {}
                    return user_dict
                return None
    
    async def verify_password(self, user_id: int, password: str) -> bool:
        """Verify user password
        
        Args:
            user_id: User ID
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT password_hash FROM users WHERE id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return False
                
                stored_hash = row[0]
                # Verify password using bcrypt
                return bcrypt.checkpw(
                    password.encode('utf-8'),
                    stored_hash.encode('utf-8')
                )
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    async def update_user_info(
        self,
        user_id: int,
        nickname: Optional[str] = None,
        avatar: Optional[str] = None,
        old_password: Optional[str] = None,
        new_password: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update user information
        
        Args:
            user_id: User ID
            nickname: New nickname (optional)
            avatar: New avatar URL (optional)
            old_password: Current password (required if changing password)
            new_password: New password (optional)
            preferences: User preferences dict (optional)
            
        Returns:
            Updated user data dict
            
        Raises:
            HTTPException: If user not found or password verification fails
        """
        # Verify user exists
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # Verify old password if changing password
        if new_password:
            if not old_password:
                raise HTTPException(status_code=400, detail="old_password is required when changing password")
            
            if not await self.verify_password(user_id, old_password):
                raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if nickname is not None:
            update_fields.append("nickname = ?")
            params.append(nickname)
        
        if avatar is not None:
            update_fields.append("avatar = ?")
            params.append(avatar)
        
        if new_password is not None:
            update_fields.append("password_hash = ?")
            params.append(self._hash_password(new_password))
        
        if preferences is not None:
            update_fields.append("preferences = ?")
            params.append(json.dumps(preferences))
        
        if not update_fields:
            # No fields to update, return current user
            return user
        
        # Add updated_at timestamp
        update_fields.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        
        # Add user_id for WHERE clause
        params.append(user_id)
        
        # Execute update
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(query, params)
                await db.commit()
                logger.info(f"User {user_id} information updated successfully")
            except Exception as e:
                logger.exception(f"Failed to update user {user_id}: {e}")
                raise HTTPException(status_code=500, detail="Failed to update user information")
        
        # Return updated user data
        updated_user = await self.get_user_by_id(user_id)
        return updated_user
    
    async def update_preferences(
        self,
        user_id: int,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user preferences (merge with existing)
        
        Args:
            user_id: User ID
            preferences: Preferences dict to merge
            
        Returns:
            Updated user data dict
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # Merge with existing preferences
        current_prefs = user.get('preferences') or {}
        merged_prefs = {**current_prefs, **preferences}
        
        return await self.update_user_info(
            user_id=user_id,
            preferences=merged_prefs
        )