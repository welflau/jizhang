import aiosqlite
import bcrypt
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class UserService:
    """User service for database operations"""
    
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
    
    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User data dict or None if not found
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT id, username, email, nickname, avatar, preferences, created_at, updated_at "
                "FROM users WHERE id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                
                user_dict = dict(row)
                # Parse preferences JSON
                if user_dict.get('preferences'):
                    try:
                        user_dict['preferences'] = json.loads(user_dict['preferences'])
                    except json.JSONDecodeError:
                        user_dict['preferences'] = {}
                return user_dict
    
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
                return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    
    async def update_user(
        self,
        user_id: int,
        nickname: Optional[str] = None,
        avatar: Optional[str] = None,
        new_password: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update user profile
        
        Args:
            user_id: User ID
            nickname: New nickname (optional)
            avatar: New avatar URL (optional)
            new_password: New password plain text (optional, will be hashed)
            preferences: User preferences dict (optional)
            
        Returns:
            Updated user data
            
        Raises:
            HTTPException: If user not found or update fails
        """
        # Build dynamic UPDATE query
        update_fields = []
        params = []
        
        if nickname is not None:
            update_fields.append("nickname = ?")
            params.append(nickname)
        
        if avatar is not None:
            update_fields.append("avatar = ?")
            params.append(avatar)
        
        if new_password is not None:
            # Hash password with bcrypt
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(rounds=10))
            update_fields.append("password_hash = ?")
            params.append(password_hash.decode('utf-8'))
        
        if preferences is not None:
            update_fields.append("preferences = ?")
            params.append(json.dumps(preferences))
        
        if not update_fields:
            # No fields to update, return current user
            user = await self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            return user
        
        # Add updated_at timestamp
        update_fields.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        
        # Add user_id for WHERE clause
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                await db.execute(query, params)
                await db.commit()
                
                # Fetch updated user
                updated_user = await self.get_user_by_id(user_id)
                if not updated_user:
                    raise HTTPException(status_code=404, detail=f"User {user_id} not found after update")
                
                logger.info(f"User {user_id} profile updated successfully")
                return updated_user
        
        except aiosqlite.IntegrityError as e:
            logger.error(f"Database integrity error updating user {user_id}: {e}")
            raise HTTPException(status_code=400, detail="Invalid update data")
        except Exception as e:
            logger.exception(f"Error updating user {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to update user profile")