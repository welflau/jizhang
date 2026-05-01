from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Category(Base):
    """分类模型"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="分类名称")
    type = Column(String(10), nullable=False, comment="分类类型: income/expense")
    icon = Column(String(50), nullable=True, comment="图标名称")
    color = Column(String(20), nullable=True, comment="颜色代码")
    user_id = Column(Integer, nullable=True, comment="用户ID，NULL表示系统默认分类")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}')>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "icon": self.icon,
            "color": self.color,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }