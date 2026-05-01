from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class LoginMethod(str, enum.Enum):
    """登录方式枚举"""
    EMAIL = "email"
    PHONE = "phone"


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # 用户信息
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # 状态字段
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # 登录方式
    login_method = Column(SQLEnum(LoginMethod), default=LoginMethod.EMAIL, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # 密码重置
    reset_token = Column(String(255), nullable=True, unique=True)
    reset_token_expires_at = Column(DateTime, nullable=True)
    
    # 邮箱/手机验证
    verification_token = Column(String(255), nullable=True, unique=True)
    verification_token_expires_at = Column(DateTime, nullable=True)
    
    # 关系
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

    @property
    def is_active(self):
        """检查用户是否激活"""
        return self.status == UserStatus.ACTIVE

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "email": self.email,
            "phone": self.phone,
            "username": self.username,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "status": self.status.value,
            "is_verified": self.is_verified,
            "is_superuser": self.is_superuser,
            "login_method": self.login_method.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }


class RefreshToken(Base):
    """刷新令牌模型"""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    
    # 设备信息
    device_info = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # 状态
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_used_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, is_revoked={self.is_revoked})>"

    @property
    def is_expired(self):
        """检查令牌是否过期"""
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self):
        """检查令牌是否有效"""
        return not self.is_revoked and not self.is_expired

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "device_info": self.device_info,
            "ip_address": self.ip_address,
            "is_revoked": self.is_revoked,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
        }


class LoginHistory(Base):
    """登录历史模型"""
    __tablename__ = "login_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # 登录信息
    login_method = Column(SQLEnum(LoginMethod), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_info = Column(String(500), nullable=True)
    location = Column(String(200), nullable=True)
    
    # 登录结果
    success = Column(Boolean, default=True, nullable=False)
    failure_reason = Column(String(200), nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<LoginHistory(id={self.id}, user_id={self.user_id}, success={self.success})>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "login_method": self.login_method.value,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "device_info": self.device_info,
            "location": self.location,
            "success": self.success,
            "failure_reason": self.failure_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }