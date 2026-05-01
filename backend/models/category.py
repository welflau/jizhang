"""Category model for income/expense classification.

Fields:
    - id: Primary key
    - user_id: Foreign key to users table (CASCADE delete)
    - name: Category display name (max 50 chars)
    - type: Enum('income', 'expense') for transaction type
    - icon: Optional icon identifier (e.g., 'food', 'transport')
    - color: Optional hex color code for UI display
    - created_at: Category creation timestamp
    - updated_at: Last modification timestamp

Constraints:
    - Unique(user_id, name): Prevent duplicate category names per user
    - CHECK(type IN ('income', 'expense')): Enforce valid type values

Relationships:
    - user: Owner of this category
    - transactions: Transactions tagged with this category
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .base import Base


class CategoryType(enum.Enum):
    """Enum for category type validation."""
    income = "income"
    expense = "expense"


class Category(Base):
    """User-defined category for transaction classification."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to user (CASCADE delete when user is deleted)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Owner user ID (cascades on delete)"
    )
    
    # Category display name (unique per user)
    name = Column(
        String(50),
        nullable=False,
        comment="Category display name (max 50 chars)"
    )
    
    # Type constraint using Enum for database-level validation
    type = Column(
        Enum(CategoryType),
        nullable=False,
        comment="Transaction type: 'income' or 'expense'"
    )
    
    # Optional UI customization fields
    icon = Column(
        String(30),
        nullable=True,
        comment="Icon identifier (e.g., 'food', 'salary')"
    )
    color = Column(
        String(7),
        nullable=True,
        comment="Hex color code (e.g., '#FF5733')"
    )
    
    # Audit timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="Category creation timestamp"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last modification timestamp"
    )

    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship(
        "Transaction",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_category_name"),
        Index("idx_category_user_type", "user_id", "type"),
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, user_id={self.user_id}, name='{self.name}', type={self.type.value})>"
