from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.schemas.user import UserCreate, UserUpdate, UserPreferences


class UserService:
    """用户服务类，处理用户相关的业务逻辑"""

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据用户ID获取用户信息"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """根据邮箱获取用户信息"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户信息"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """创建新用户"""
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise ValueError("用户名或邮箱已存在")

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        update_data = user_data.dict(exclude_unset=True)
        
        # 检查邮箱是否已被其他用户使用
        if "email" in update_data:
            existing_user = UserService.get_user_by_email(db, update_data["email"])
            if existing_user and existing_user.id != user_id:
                raise ValueError("邮箱已被使用")

        # 检查用户名是否已被其他用户使用
        if "username" in update_data:
            existing_user = UserService.get_user_by_username(db, update_data["username"])
            if existing_user and existing_user.id != user_id:
                raise ValueError("用户名已被使用")

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db_user.updated_at = datetime.utcnow()

        try:
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise ValueError("更新失败，数据冲突")

    @staticmethod
    def change_password(
        db: Session, 
        user_id: int, 
        old_password: str, 
        new_password: str
    ) -> bool:
        """修改用户密码"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False

        # 验证旧密码
        if not verify_password(old_password, db_user.hashed_password):
            raise ValueError("原密码错误")

        # 设置新密码
        db_user.hashed_password = get_password_hash(new_password)
        db_user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_user)
        return True

    @staticmethod
    def update_user_preferences(
        db: Session, 
        user_id: int, 
        preferences: UserPreferences
    ) -> Optional[User]:
        """更新用户偏好设置"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        # 将偏好设置转换为字典存储
        preferences_dict = preferences.dict()
        db_user.preferences = preferences_dict
        db_user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_preferences(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户偏好设置"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        return db_user.preferences or {}

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """删除用户（软删除）"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False

        db_user.is_active = False
        db_user.updated_at = datetime.utcnow()

        db.commit()
        return True

    @staticmethod
    def activate_user(db: Session, user_id: int) -> bool:
        """激活用户"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False

        db_user.is_active = True
        db_user.updated_at = datetime.utcnow()

        db.commit()
        return True

    @staticmethod
    def update_avatar(db: Session, user_id: int, avatar_url: str) -> Optional[User]:
        """更新用户头像"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        db_user.avatar = avatar_url
        db_user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户完整资料"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        return {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "avatar": db_user.avatar,
            "bio": db_user.bio,
            "phone": db_user.phone,
            "location": db_user.location,
            "website": db_user.website,
            "is_active": db_user.is_active,
            "preferences": db_user.preferences or {},
            "created_at": db_user.created_at.isoformat() if db_user.created_at else None,
            "updated_at": db_user.updated_at.isoformat() if db_user.updated_at else None,
        }

    @staticmethod
    def update_last_login(db: Session, user_id: int) -> None:
        """更新用户最后登录时间"""
        db_user = UserService.get_user_by_id(db, user_id)
        if db_user:
            db_user.last_login = datetime.utcnow()
            db.commit()

    @staticmethod
    def verify_user_password(db: Session, user_id: int, password: str) -> bool:
        """验证用户密码"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False
        return verify_password(password, db_user.hashed_password)

    @staticmethod
    def update_user_settings(
        db: Session, 
        user_id: int, 
        settings: Dict[str, Any]
    ) -> Optional[User]:
        """更新用户设置"""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        # 合并现有设置和新设置
        current_preferences = db_user.preferences or {}
        current_preferences.update(settings)
        
        db_user.preferences = current_preferences
        db_user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def check_email_exists(db: Session, email: str, exclude_user_id: Optional[int] = None) -> bool:
        """检查邮箱是否已存在"""
        query = db.query(User).filter(User.email == email)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is not None

    @staticmethod
    def check_username_exists(db: Session, username: str, exclude_user_id: Optional[int] = None) -> bool:
        """检查用户名是否已存在"""
        query = db.query(User).filter(User.username == username)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is not None