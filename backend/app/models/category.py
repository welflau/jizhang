from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class TransactionType(str, enum.Enum):
    """交易类型枚举"""
    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):
    """分类模型"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, index=True)
    type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
    description = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关联关系
    # transactions = relationship("Transaction", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}', user_id={self.user_id})>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "icon": self.icon,
            "color": self.color,
            "description": self.description,
            "is_active": self.is_active,
            "sort_order": self.sort_order,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def create_default_categories(cls, user_id: int):
        """创建默认分类"""
        default_income_categories = [
            {"name": "工资", "icon": "💰", "color": "#4CAF50", "sort_order": 1},
            {"name": "奖金", "icon": "🎁", "color": "#8BC34A", "sort_order": 2},
            {"name": "投资收益", "icon": "📈", "color": "#009688", "sort_order": 3},
            {"name": "兼职", "icon": "💼", "color": "#00BCD4", "sort_order": 4},
            {"name": "其他收入", "icon": "💵", "color": "#03A9F4", "sort_order": 5}
        ]
        
        default_expense_categories = [
            {"name": "餐饮", "icon": "🍔", "color": "#FF5722", "sort_order": 1},
            {"name": "交通", "icon": "🚗", "color": "#FF9800", "sort_order": 2},
            {"name": "购物", "icon": "🛍️", "color": "#FFC107", "sort_order": 3},
            {"name": "娱乐", "icon": "🎮", "color": "#FFEB3B", "sort_order": 4},
            {"name": "住房", "icon": "🏠", "color": "#9C27B0", "sort_order": 5},
            {"name": "医疗", "icon": "💊", "color": "#E91E63", "sort_order": 6},
            {"name": "教育", "icon": "📚", "color": "#3F51B5", "sort_order": 7},
            {"name": "通讯", "icon": "📱", "color": "#2196F3", "sort_order": 8},
            {"name": "其他支出", "icon": "💸", "color": "#607D8B", "sort_order": 9}
        ]
        
        categories = []
        
        for cat_data in default_income_categories:
            categories.append(cls(
                name=cat_data["name"],
                type=TransactionType.INCOME,
                icon=cat_data["icon"],
                color=cat_data["color"],
                sort_order=cat_data["sort_order"],
                user_id=user_id,
                is_active=True
            ))
        
        for cat_data in default_expense_categories:
            categories.append(cls(
                name=cat_data["name"],
                type=TransactionType.EXPENSE,
                icon=cat_data["icon"],
                color=cat_data["color"],
                sort_order=cat_data["sort_order"],
                user_id=user_id,
                is_active=True
            ))
        
        return categories

    def validate(self):
        """验证分类数据"""
        errors = []
        
        if not self.name or len(self.name.strip()) == 0:
            errors.append("分类名称不能为空")
        elif len(self.name) > 50:
            errors.append("分类名称不能超过50个字符")
        
        if not self.type:
            errors.append("分类类型不能为空")
        elif self.type not in [TransactionType.INCOME, TransactionType.EXPENSE]:
            errors.append("分类类型必须是 income 或 expense")
        
        if self.icon and len(self.icon) > 50:
            errors.append("图标不能超过50个字符")
        
        if self.color and len(self.color) > 20:
            errors.append("颜色不能超过20个字符")
        
        if self.description and len(self.description) > 200:
            errors.append("描述不能超过200个字符")
        
        if self.sort_order is not None and self.sort_order < 0:
            errors.append("排序值不能为负数")
        
        return errors