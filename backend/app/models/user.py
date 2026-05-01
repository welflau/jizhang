from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(50), nullable=True, comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    phone = Column(String(20), nullable=True, comment="手机号")
    bio = Column(Text, nullable=True, comment="个人简介")
    gender = Column(String(10), nullable=True, comment="性别")
    birthday = Column(DateTime, nullable=True, comment="生日")
    location = Column(String(100), nullable=True, comment="所在地")
    
    # 偏好设置
    theme = Column(String(20), default="light", comment="主题设置: light/dark")
    language = Column(String(10), default="zh-CN", comment="语言设置")
    notification_enabled = Column(Boolean, default=True, comment="是否启用通知")
    email_notification = Column(Boolean, default=True, comment="是否启用邮件通知")
    
    # 账户状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_verified = Column(Boolean, default=False, comment="是否验证邮箱")
    is_admin = Column(Boolean, default=False, comment="是否管理员")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")

    def set_password(self, password: str) -> None:
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """转换为字典"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "nickname": self.nickname,
            "avatar": self.avatar,
            "phone": self.phone,
            "bio": self.bio,
            "gender": self.gender,
            "birthday": self.birthday.isoformat() if self.birthday else None,
            "location": self.location,
            "theme": self.theme,
            "language": self.language,
            "notification_enabled": self.notification_enabled,
            "email_notification": self.email_notification,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
        
        if include_sensitive:
            data["password_hash"] = self.password_hash
            
        return data

    def update_profile(self, **kwargs) -> None:
        """更新用户资料"""
        allowed_fields = [
            "nickname", "avatar", "phone", "bio", 
            "gender", "birthday", "location"
        ]
        for field in allowed_fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])
        self.updated_at = datetime.utcnow()

    def update_preferences(self, **kwargs) -> None:
        """更新用户偏好设置"""
        allowed_fields = [
            "theme", "language", 
            "notification_enabled", "email_notification"
        ]
        for field in allowed_fields:
            if field in kwargs:
                setattr(self, field, kwargs[field])
        self.updated_at = datetime.utcnow()

    def update_last_login(self) -> None:
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"