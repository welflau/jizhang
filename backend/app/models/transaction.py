from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class TransactionType(enum.Enum):
    """交易类型枚举"""
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(Base):
    """交易记录模型"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, comment="交易记录ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID")
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True, comment="分类ID")
    type = Column(SQLEnum(TransactionType), nullable=False, index=True, comment="交易类型：收入/支出")
    amount = Column(Numeric(15, 2), nullable=False, comment="交易金额")
    description = Column(String(500), nullable=True, comment="交易描述")
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True, comment="交易日期")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, type={self.type.value}, amount={self.amount})>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "type": self.type.value,
            "amount": float(self.amount),
            "description": self.description,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "category": self.category.to_dict() if self.category else None
        }