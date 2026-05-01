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
    icon = Column(String(50), default="📁")
    color = Column(String(20), default="#1a1a2e")
    description = Column(String(200))
    is_active = Column(Boolean, default=True, index=True)
    is_system = Column(Boolean, default=False)  # 系统预设分类不可删除
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联关系
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}')>"
    
    def to_dict(self, include_transactions=False):
        """转换为字典"""
        data = {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "icon": self.icon,
            "color": self.color,
            "description": self.description,
            "is_active": self.is_active,
            "is_system": self.is_system,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_transactions:
            data["transactions_count"] = len(self.transactions)
            data["transactions"] = [t.to_dict() for t in self.transactions]
        
        return data
    
    @classmethod
    def get_default_categories(cls):
        """获取默认分类列表"""
        return [
            # 收入分类
            {
                "name": "工资",
                "type": TransactionType.INCOME,
                "icon": "💰",
                "color": "#2ecc71",
                "description": "工资收入",
                "is_system": True,
                "sort_order": 1
            },
            {
                "name": "奖金",
                "type": TransactionType.INCOME,
                "icon": "🎁",
                "color": "#27ae60",
                "description": "奖金收入",
                "is_system": True,
                "sort_order": 2
            },
            {
                "name": "投资收益",
                "type": TransactionType.INCOME,
                "icon": "📈",
                "color": "#16a085",
                "description": "投资理财收益",
                "is_system": True,
                "sort_order": 3
            },
            {
                "name": "其他收入",
                "type": TransactionType.INCOME,
                "icon": "💵",
                "color": "#1abc9c",
                "description": "其他收入",
                "is_system": True,
                "sort_order": 99
            },
            # 支出分类
            {
                "name": "餐饮",
                "type": TransactionType.EXPENSE,
                "icon": "🍔",
                "color": "#e74c3c",
                "description": "餐饮支出",
                "is_system": True,
                "sort_order": 1
            },
            {
                "name": "交通",
                "type": TransactionType.EXPENSE,
                "icon": "🚗",
                "color": "#c0392b",
                "description": "交通出行",
                "is_system": True,
                "sort_order": 2
            },
            {
                "name": "购物",
                "type": TransactionType.EXPENSE,
                "icon": "🛍️",
                "color": "#e67e22",
                "description": "购物消费",
                "is_system": True,
                "sort_order": 3
            },
            {
                "name": "娱乐",
                "type": TransactionType.EXPENSE,
                "icon": "🎮",
                "color": "#d35400",
                "description": "娱乐休闲",
                "is_system": True,
                "sort_order": 4
            },
            {
                "name": "医疗",
                "type": TransactionType.EXPENSE,
                "icon": "🏥",
                "color": "#9b59b6",
                "description": "医疗健康",
                "is_system": True,
                "sort_order": 5
            },
            {
                "name": "教育",
                "type": TransactionType.EXPENSE,
                "icon": "📚",
                "color": "#8e44ad",
                "description": "教育培训",
                "is_system": True,
                "sort_order": 6
            },
            {
                "name": "住房",
                "type": TransactionType.EXPENSE,
                "icon": "🏠",
                "color": "#3498db",
                "description": "房租房贷",
                "is_system": True,
                "sort_order": 7
            },
            {
                "name": "通讯",
                "type": TransactionType.EXPENSE,
                "icon": "📱",
                "color": "#2980b9",
                "description": "通讯费用",
                "is_system": True,
                "sort_order": 8
            },
            {
                "name": "其他支出",
                "type": TransactionType.EXPENSE,
                "icon": "💸",
                "color": "#95a5a6",
                "description": "其他支出",
                "is_system": True,
                "sort_order": 99
            }
        ]