from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    period = Column(String(7), nullable=False)  # Format: YYYY-MM
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")

    # Indexes for query optimization
    __table_args__ = (
        Index("ix_budgets_user_id", "user_id"),
        Index("ix_budgets_period", "period"),
        Index("ix_budgets_user_id_period", "user_id", "period"),
        Index("ix_budgets_user_id_category_id_period", "user_id", "category_id", "period", unique=True),
    )

    def __repr__(self):
        return f"<Budget(id={self.id}, user_id={self.user_id}, category_id={self.category_id}, amount={self.amount}, period={self.period})>"