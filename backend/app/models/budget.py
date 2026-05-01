from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    period = Column(String(7), nullable=False, comment="预算周期，格式 YYYY-MM")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")

    # 索引
    __table_args__ = (
        Index("idx_budget_user_id", "user_id"),
        Index("idx_budget_period", "period"),
        Index("idx_budget_user_period", "user_id", "period"),
        Index("idx_budget_user_category_period", "user_id", "category_id", "period", unique=True),
    )

    def __repr__(self):
        return f"<Budget(id={self.id}, user_id={self.user_id}, category_id={self.category_id}, amount={self.amount}, period={self.period})>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "amount": float(self.amount) if self.amount else 0.0,
            "period": self.period,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }