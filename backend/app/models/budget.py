from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Float, nullable=False)
    period = Column(String(7), nullable=False)  # Format: YYYY-MM
    spent = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category")

    # Indexes
    __table_args__ = (
        Index('idx_user_period', 'user_id', 'period'),
        Index('idx_user_category_period', 'user_id', 'category_id', 'period', unique=True),
    )

    def to_dict(self):
        """Convert budget to dictionary with usage percentage"""
        usage_percentage = (self.spent / self.amount * 100) if self.amount > 0 else 0
        
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "amount": self.amount,
            "period": self.period,
            "spent": self.spent,
            "remaining": self.amount - self.spent,
            "usage_percentage": round(usage_percentage, 2),
            "is_exceeded": self.spent > self.amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Budget(id={self.id}, user_id={self.user_id}, category_id={self.category_id}, period={self.period}, amount={self.amount}, spent={self.spent})>"