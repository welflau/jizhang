"""User model for authentication and user management.

Fields:
    - id: Primary key
    - username: Unique login identifier (3-30 chars, indexed for fast lookup)
    - email: Unique email address (indexed, validated format)
    - password_hash: Bcrypt hashed password (255 chars to accommodate hash output)
    - created_at: Account creation timestamp
    - updated_at: Last modification timestamp

Relationships:
    - categories: User's custom income/expense categories
    - transactions: User's financial transaction records
    - payment_methods: User's payment method configurations
"""

from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    """User account model with authentication credentials."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Unique username for login (indexed for performance)
    username = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique login identifier (3-30 characters)"
    )
    
    # Unique email for account recovery (indexed for lookup)
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique email address for notifications"
    )
    
    # Bcrypt hash requires 60 chars, use 255 for future-proofing
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Bcrypt hashed password (never store plaintext)"
    )
    
    # Audit timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="Account creation timestamp"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last profile update timestamp"
    )

    # Relationships (cascade delete to clean up user data)
    categories = relationship(
        "Category",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    transactions = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    payment_methods = relationship(
        "PaymentMethod",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Composite index for common query patterns
    __table_args__ = (
        Index("idx_user_email_username", "email", "username"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
