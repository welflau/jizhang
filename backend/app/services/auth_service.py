import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, PasswordChange

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """认证服务类"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希值"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """解码令牌"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的Token",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """认证用户"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        if AuthService.get_user_by_username(db, user_create.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        if AuthService.get_user_by_email(db, user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )

        hashed_password = AuthService.get_password_hash(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            is_active=True,
            is_superuser=False
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
        """更新用户信息"""
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        update_data = user_update.dict(exclude_unset=True)
        
        # 检查邮箱是否被其他用户使用
        if "email" in update_data:
            existing_user = AuthService.get_user_by_email(db, update_data["email"])
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被其他用户使用"
                )

        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_password(db: Session, user_id: int, password_change: PasswordChange) -> bool:
        """修改密码"""
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        # 验证旧密码
        if not AuthService.verify_password(password_change.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="原密码错误"
            )

        # 设置新密码
        user.hashed_password = AuthService.get_password_hash(password_change.new_password)
        db.commit()
        return True

    @staticmethod
    def update_user_preferences(db: Session, user_id: int, preferences: Dict[str, Any]) -> User:
        """更新用户偏好设置"""
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        user.preferences = preferences
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_preferences(db: Session, user_id: int) -> Dict[str, Any]:
        """获取用户偏好设置"""
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return user.preferences or {}

    @staticmethod
    def update_last_login(db: Session, user_id: int) -> None:
        """更新最后登录时间"""
        user = AuthService.get_user_by_id(db, user_id)
        if user:
            user.last_login = datetime.utcnow()
            db.commit()

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> User:
        """停用用户"""
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def activate_user(db: Session, user_id: int) -> User:
        """激活用户"""
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        user.is_active = True
        db.commit()
        db.refresh(user)
        return user