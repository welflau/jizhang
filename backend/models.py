"""SQLAlchemy ORM models for core database tables.

Defines User, Category, Transaction, and PaymentMethod models with proper
relationships and constraints.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class CategoryType(str, enum.Enum):
    """Category type enumeration."""

    INCOME = "income"
    EXPENSE = "expense"


class PaymentMethodType(str, enum.Enum):
    """Payment method type enumeration."""

    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    E_WALLET = "e_wallet"
    OTHER = "other"


class User(Base):
    """User account model.

    Attributes:
        id: Primary key
        username: Unique username (3-30 chars)
        email: Unique email address
        password_hash: Hashed password (never store plaintext)
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    categories = relationship(
        "Category", back_populates="user", cascade="all, delete-orphan"
    )
    transactions = relationship(
        "Transaction", back_populates="user", cascade="all, delete-orphan"
    )
    payment_methods = relationship(
        "PaymentMethod", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Category(Base):
    """Transaction category model.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        name: Category name (e.g., 'Salary', 'Food', 'Transport')
        type: CategoryType enum (income/expense)
        icon: Icon identifier (e.g., 'icon-food', 'icon-salary')
        color: Hex color code (e.g., '#FF5733')
        created_at: Creation timestamp
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    type = Column(SQLEnum(CategoryType), nullable=False, index=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color: #RRGGBB
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship(
        "Transaction", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type.value}')>"


class PaymentMethod(Base):
    """Payment method model.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        name: Payment method name (e.g., 'My Visa Card', 'Cash Wallet')
        type: PaymentMethodType enum
        created_at: Creation timestamp
    """

    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(SQLEnum(PaymentMethodType), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="payment_methods")
    transactions = relationship("Transaction", back_populates="payment_method")

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, name='{self.name}', type='{self.type.value}')>"


class Transaction(Base):
    """Financial transaction model.

    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        category_id: Foreign key to categories table
        payment_method_id: Foreign key to payment_methods table (nullable)
        amount: Transaction amount (Decimal for precision)
        date: Transaction date
        description: Optional transaction description
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(
        Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    payment_method_id = Column(
        Integer, ForeignKey("payment_methods.id", ondelete="SET NULL"), nullable=True, index=True
    )
    amount = Column(Numeric(15, 2), nullable=False)  # Precision: 15 digits, 2 decimals
    date = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    payment_method = relationship("PaymentMethod", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, date='{self.date}', category_id={self.category_id})>"
