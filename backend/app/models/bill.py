from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Index, Text
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base


class BillType(str, enum.Enum):
    """账单类型枚举"""
    INCOME = "income"  # 收入
    EXPENSE = "expense"  # 支出


class Bill(Base):
    """账单模型"""
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True, comment="账单ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    
    # 账单基本信息
    type = Column(Enum(BillType), nullable=False, comment="账单类型：收入/支出")
    category_id = Column(Integer, nullable=False, comment="分类ID")
    amount = Column(Float, nullable=False, comment="金额")
    
    # 账单详细信息
    description = Column(String(500), nullable=True, comment="账单描述")
    note = Column(Text, nullable=True, comment="备注")
    
    # 时间信息
    bill_date = Column(DateTime, nullable=False, default=datetime.utcnow, comment="账单日期")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 其他信息
    tags = Column(String(500), nullable=True, comment="标签，逗号分隔")
    is_deleted = Column(Integer, default=0, comment="是否删除：0-否，1-是")

    # 定义复合索引以优化查询性能
    __table_args__ = (
        # 用户+时间索引（最常用的查询组合）
        Index('idx_user_bill_date', 'user_id', 'bill_date'),
        
        # 用户+类型+时间索引（按类型筛选时间范围）
        Index('idx_user_type_date', 'user_id', 'type', 'bill_date'),
        
        # 用户+分类+时间索引（按分类筛选时间范围）
        Index('idx_user_category_date', 'user_id', 'category_id', 'bill_date'),
        
        # 用户+金额索引（金额范围查询）
        Index('idx_user_amount', 'user_id', 'amount'),
        
        # 用户+类型+分类索引（组合筛选）
        Index('idx_user_type_category', 'user_id', 'type', 'category_id'),
        
        # 用户+删除状态+时间索引（排除已删除记录）
        Index('idx_user_deleted_date', 'user_id', 'is_deleted', 'bill_date'),
        
        # 创建时间索引（用于按创建时间排序）
        Index('idx_created_at', 'created_at'),
        
        {'comment': '账单表'}
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type.value if self.type else None,
            "category_id": self.category_id,
            "amount": self.amount,
            "description": self.description,
            "note": self.note,
            "bill_date": self.bill_date.isoformat() if self.bill_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "tags": self.tags.split(",") if self.tags else [],
            "is_deleted": self.is_deleted
        }

    def __repr__(self):
        return f"<Bill(id={self.id}, user_id={self.user_id}, type={self.type}, amount={self.amount})>"