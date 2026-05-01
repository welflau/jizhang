from sqlalchemy import Column, Integer, String, Float, DateTime, Index, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class BillType(str, enum.Enum):
    """账单类型枚举"""
    INCOME = "income"  # 收入
    EXPENSE = "expense"  # 支出


class Bill(Base):
    """账单模型"""
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True, comment="账单ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, comment="分类ID")
    type = Column(SQLEnum(BillType), nullable=False, comment="账单类型：收入/支出")
    amount = Column(Float, nullable=False, comment="金额")
    description = Column(String(500), nullable=True, comment="描述")
    bill_date = Column(DateTime, nullable=False, default=datetime.utcnow, comment="账单日期")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="bills")
    category = relationship("Category", back_populates="bills")

    # 数据库索引优化
    __table_args__ = (
        # 单字段索引
        Index("idx_bill_user_id", "user_id"),
        Index("idx_bill_category_id", "category_id"),
        Index("idx_bill_type", "type"),
        Index("idx_bill_amount", "amount"),
        Index("idx_bill_date", "bill_date"),
        Index("idx_bill_created_at", "created_at"),
        
        # 复合索引 - 优化常见查询组合
        Index("idx_bill_user_date", "user_id", "bill_date"),
        Index("idx_bill_user_type", "user_id", "type"),
        Index("idx_bill_user_category", "user_id", "category_id"),
        Index("idx_bill_user_type_date", "user_id", "type", "bill_date"),
        Index("idx_bill_user_category_date", "user_id", "category_id", "bill_date"),
        Index("idx_bill_user_type_category_date", "user_id", "type", "category_id", "bill_date"),
        
        # 金额范围查询优化
        Index("idx_bill_user_amount", "user_id", "amount"),
        Index("idx_bill_user_type_amount", "user_id", "type", "amount"),
    )

    def __repr__(self):
        return f"<Bill(id={self.id}, user_id={self.user_id}, type={self.type}, amount={self.amount}, date={self.bill_date})>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "type": self.type.value,
            "amount": self.amount,
            "description": self.description,
            "bill_date": self.bill_date.isoformat() if self.bill_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def get_statistics_by_type(cls, session, user_id, start_date=None, end_date=None):
        """按类型统计金额"""
        from sqlalchemy import func
        
        query = session.query(
            cls.type,
            func.sum(cls.amount).label("total_amount"),
            func.count(cls.id).label("count")
        ).filter(cls.user_id == user_id)
        
        if start_date:
            query = query.filter(cls.bill_date >= start_date)
        if end_date:
            query = query.filter(cls.bill_date <= end_date)
        
        return query.group_by(cls.type).all()

    @classmethod
    def get_statistics_by_category(cls, session, user_id, bill_type=None, start_date=None, end_date=None):
        """按分类统计金额"""
        from sqlalchemy import func
        
        query = session.query(
            cls.category_id,
            func.sum(cls.amount).label("total_amount"),
            func.count(cls.id).label("count")
        ).filter(cls.user_id == user_id)
        
        if bill_type:
            query = query.filter(cls.type == bill_type)
        if start_date:
            query = query.filter(cls.bill_date >= start_date)
        if end_date:
            query = query.filter(cls.bill_date <= end_date)
        
        return query.group_by(cls.category_id).all()

    @classmethod
    def get_daily_statistics(cls, session, user_id, start_date=None, end_date=None):
        """按日期统计金额"""
        from sqlalchemy import func, cast, Date
        
        query = session.query(
            cast(cls.bill_date, Date).label("date"),
            cls.type,
            func.sum(cls.amount).label("total_amount"),
            func.count(cls.id).label("count")
        ).filter(cls.user_id == user_id)
        
        if start_date:
            query = query.filter(cls.bill_date >= start_date)
        if end_date:
            query = query.filter(cls.bill_date <= end_date)
        
        return query.group_by(cast(cls.bill_date, Date), cls.type).order_by(cast(cls.bill_date, Date)).all()