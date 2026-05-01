"""Transaction model for financial record tracking.

Fields:
    - id: Primary key
    - user_id: Foreign key to users table (CASCADE delete)
    - category_id: Foreign key to categories table (SET NULL on delete)
    - payment_method_id: Foreign key to payment_methods table (SET NULL on delete)
    - amount: Decimal(10,2) for precise currency storage
    - date: Transaction date (indexed for time-range queries)
    - description: Optional transaction note (max 500 chars)
    - created_at: Record creation timestamp
    - updated_at: Last modification timestamp

Constraints:
    - amount > 0: Enforce positive transaction amounts
    - date <= today: Prevent future-dated transactions

Relationships:
    - user: Owner of this transaction
    - category: Classification category (nullable if category deleted)
    - payment_method: Payment method used (nullable if method deleted)
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Date, Index, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Transaction(Base):
    """Financial transaction record with category and payment method."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to user (CASCADE delete when user is deleted)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Owner user ID (cascades on delete)"
    )
    
    # Foreign key to category (SET NULL if category deleted, allow recategorization)
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Category ID (nullable if category deleted)"
    )
    
    # Foreign key to payment method (SET NULL if method deleted)
    payment_method_id = Column(
        Integer,
        ForeignKey("payment_methods.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Payment method ID (nullable if method deleted)"
    )
    
    # Amount stored as Numeric(10,2) for precise currency calculations
    # Supports up to 99,999,999.99 (10 digits total, 2 decimal places)
    amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Transaction amount (precise decimal, max 99,999,999.99)"
    )
    
    # Transaction date (indexed for time-range queries)
    date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Transaction date (indexed for reporting)"
    )
    
    # Optional description/note
    description = Column(
        String(500),
        nullable=True,
        comment="Optional transaction note (max 500 chars)"
    )
    
    # Audit timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="Record creation timestamp"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last modification timestamp"
    )

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    payment_method = relationship("PaymentMethod", back_populates="transactions")

    # Constraints and indexes
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transaction_amount_positive"),
        Index("idx_transaction_user_date", "user_id", "date"),
        Index("idx_transaction_category", "category_id"),
    )

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, date={self.date})>"
