from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


class TransactionType(str, enum.Enum):
    """交易类型枚举"""
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(Base):
    """收支记录模型"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, comment="交易记录ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    type = Column(SQLEnum(TransactionType), nullable=False, comment="交易类型：income收入/expense支出")
    amount = Column(Numeric(precision=15, scale=2), nullable=False, comment="金额")
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, comment="分类ID")
    date = Column(DateTime, nullable=False, default=datetime.utcnow, comment="交易日期")
    note = Column(String(500), nullable=True, comment="备注说明")
    payment_method = Column(String(50), nullable=True, comment="支付方式")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系定义
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    # 创建复合索引优化查询性能
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'date'),
        Index('idx_user_type', 'user_id', 'type'),
        Index('idx_user_category', 'user_id', 'category_id'),
        Index('idx_user_type_date', 'user_id', 'type', 'date'),
        Index('idx_date', 'date'),
        {'comment': '收支记录表'}
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, type={self.type}, amount={self.amount})>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type.value if isinstance(self.type, TransactionType) else self.type,
            "amount": float(self.amount) if self.amount else 0,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "date": self.date.isoformat() if self.date else None,
            "note": self.note,
            "payment_method": self.payment_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }