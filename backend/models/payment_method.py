"""PaymentMethod model for payment method management.

Fields:
    - id: Primary key
    - user_id: Foreign key to users table (CASCADE delete)
    - name: Payment method display name (max 50 chars)
    - type: Payment type (e.g., 'cash', 'credit_card', 'debit_card', 'digital_wallet')
    - created_at: Method creation timestamp
    - updated_at: Last modification timestamp

Constraints:
    - Unique(user_id, name): Prevent duplicate payment method names per user

Relationships:
    - user: Owner of this payment method
    - transactions: Transactions using this payment method
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class PaymentMethod(Base):
    """User-defined payment method for transaction tracking."""

    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to user (CASCADE delete when user is deleted)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Owner user ID (cascades on delete)"
    )
    
    # Payment method display name (unique per user)
    name = Column(
        String(50),
        nullable=False,
        comment="Payment method display name (max 50 chars)"
    )
    
    # Payment type (flexible string for extensibility)
    type = Column(
        String(30),
        nullable=False,
        comment="Payment type (e.g., 'cash', 'credit_card', 'digital_wallet')"
    )
    
    # Audit timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="Method creation timestamp"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last modification timestamp"
    )

    # Relationships
    user = relationship("User", back_populates="payment_methods")
    transactions = relationship(
        "Transaction",
        back_populates="payment_method",
        lazy="select"
    )

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_payment_method_name"),
        Index("idx_payment_method_user_type", "user_id", "type"),
    )

    def __repr__(self) -> str:
        return f"<PaymentMethod(id={self.id}, user_id={self.user_id}, name='{self.name}', type='{self.type}')>"
