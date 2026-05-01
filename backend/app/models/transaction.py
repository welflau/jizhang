from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    note = Column(String(500), nullable=True)
    payment_method = Column(String(50), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    # Indexes for query optimization
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'date'),
        Index('idx_user_type', 'user_id', 'type'),
        Index('idx_user_category', 'user_id', 'category_id'),
        Index('idx_date', 'date'),
        Index('idx_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, type={self.type}, amount={self.amount})>"

    def to_dict(self):
        """Convert transaction object to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type.value if isinstance(self.type, TransactionType) else self.type,
            "amount": float(self.amount) if self.amount else 0.0,
            "category_id": self.category_id,
            "date": self.date.isoformat() if self.date else None,
            "note": self.note,
            "payment_method": self.payment_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }