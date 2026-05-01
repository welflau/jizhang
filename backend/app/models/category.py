# backend/app/models/category.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class CategoryType(str, enum.Enum):
    """分类类型枚举"""
    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):
    """分类模型"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    type = Column(SQLEnum(CategoryType), nullable=False)
    icon = Column(String(50), default="📁")
    color = Column(String(20), default="#1a1a2e")
    is_default = Column(Boolean, default=False)
    created_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()))
    updated_at = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()), onupdate=lambda: int(datetime.utcnow().timestamp()))

    # 关系
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")

    # 索引优化
    __table_args__ = (
        Index('idx_user_type', 'user_id', 'type'),
        Index('idx_user_default', 'user_id', 'is_default'),
        Index('idx_user_name', 'user_id', 'name'),
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}', user_id={self.user_id})>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "type": self.type.value,
            "icon": self.icon,
            "color": self.color,
            "is_default": self.is_default,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def get_default_categories(cls, category_type: CategoryType):
        """获取默认分类列表"""
        if category_type == CategoryType.INCOME:
            return [
                {"name": "工资", "icon": "💰", "color": "#2ecc71"},
                {"name": "奖金", "icon": "🎁", "color": "#3498db"},
                {"name": "投资收益", "icon": "📈", "color": "#9b59b6"},
                {"name": "兼职", "icon": "💼", "color": "#1abc9c"},
                {"name": "其他收入", "icon": "💵", "color": "#16a085"}
            ]
        else:  # EXPENSE
            return [
                {"name": "餐饮", "icon": "🍔", "color": "#e74c3c"},
                {"name": "交通", "icon": "🚗", "color": "#e67e22"},
                {"name": "购物", "icon": "🛒", "color": "#f39c12"},
                {"name": "娱乐", "icon": "🎮", "color": "#9b59b6"},
                {"name": "医疗", "icon": "💊", "color": "#e91e63"},
                {"name": "教育", "icon": "📚", "color": "#3498db"},
                {"name": "住房", "icon": "🏠", "color": "#34495e"},
                {"name": "通讯", "icon": "📱", "color": "#16a085"},
                {"name": "其他支出", "icon": "💸", "color": "#95a5a6"}
            ]

    @classmethod
    def create_default_categories(cls, db_session, user_id: int):
        """为新用户创建默认分类"""
        default_categories = []
        
        # 创建收入分类
        for cat_data in cls.get_default_categories(CategoryType.INCOME):
            category = cls(
                user_id=user_id,
                name=cat_data["name"],
                type=CategoryType.INCOME,
                icon=cat_data["icon"],
                color=cat_data["color"],
                is_default=True
            )
            default_categories.append(category)
        
        # 创建支出分类
        for cat_data in cls.get_default_categories(CategoryType.EXPENSE):
            category = cls(
                user_id=user_id,
                name=cat_data["name"],
                type=CategoryType.EXPENSE,
                icon=cat_data["icon"],
                color=cat_data["color"],
                is_default=True
            )
            default_categories.append(category)
        
        db_session.add_all(default_categories)
        db_session.commit()
        
        return default_categories