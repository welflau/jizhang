from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class UserPreference(Base):
    """用户偏好设置模型"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # 通知设置
    email_notifications = Column(Boolean, default=True, comment="邮件通知")
    system_notifications = Column(Boolean, default=True, comment="系统通知")
    task_reminders = Column(Boolean, default=True, comment="任务提醒")
    
    # 显示设置
    theme = Column(String(20), default="light", comment="主题: light/dark/auto")
    language = Column(String(10), default="zh-CN", comment="语言")
    timezone = Column(String(50), default="Asia/Shanghai", comment="时区")
    date_format = Column(String(20), default="YYYY-MM-DD", comment="日期格式")
    time_format = Column(String(20), default="24h", comment="时间格式: 12h/24h")
    
    # 隐私设置
    profile_visibility = Column(String(20), default="public", comment="资料可见性: public/private/friends")
    show_email = Column(Boolean, default=False, comment="显示邮箱")
    show_phone = Column(Boolean, default=False, comment="显示手机号")
    allow_search = Column(Boolean, default=True, comment="允许被搜索")
    
    # 功能设置
    auto_save = Column(Boolean, default=True, comment="自动保存")
    page_size = Column(Integer, default=20, comment="每页显示数量")
    default_view = Column(String(20), default="list", comment="默认视图: list/grid/card")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="preference")

    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, theme={self.theme})>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email_notifications": self.email_notifications,
            "system_notifications": self.system_notifications,
            "task_reminders": self.task_reminders,
            "theme": self.theme,
            "language": self.language,
            "timezone": self.timezone,
            "date_format": self.date_format,
            "time_format": self.time_format,
            "profile_visibility": self.profile_visibility,
            "show_email": self.show_email,
            "show_phone": self.show_phone,
            "allow_search": self.allow_search,
            "auto_save": self.auto_save,
            "page_size": self.page_size,
            "default_view": self.default_view,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }