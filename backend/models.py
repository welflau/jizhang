from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class TransactionType(str, enum.Enum):
    """Transaction category type enumeration"""
    INCOME = "income"
    EXPENSE = "expense"


class PaymentMethodType(str, enum.Enum):
    """Payment method type enumeration"""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    OTHER = "other"


class User(Base):
    """User model - stores user account information
    
    Attributes:
        id: Primary key, auto-increment
        username: Unique username, 3-30 characters
        email: Unique email address, max 100 characters
        password_hash: Hashed password, max 255 characters
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    payment_methods = relationship("PaymentMethod", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Category(Base):
    """Category model - stores income/expense categories
    
    Attributes:
        id: Primary key, auto-increment
        user_id: Foreign key to users table
        name: Category name, max 50 characters
        type: Category type (income/expense)
        icon: Icon identifier, max 50 characters
        color: Color hex code, max 7 characters (e.g., #FF5733)
        created_at: Category creation timestamp
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    icon = Column(String(50), nullable=True, default="default")
    color = Column(String(7), nullable=True, default="#6B7280")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type.value}')>"


class PaymentMethod(Base):
    """Payment method model - stores user payment methods
    
    Attributes:
        id: Primary key, auto-increment
        user_id: Foreign key to users table
        name: Payment method name, max 50 characters
        type: Payment method type (cash/card/etc.)
        created_at: Payment method creation timestamp
    """
    __tablename__ = "payment_methods"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    type = Column(SQLEnum(PaymentMethodType), nullable=False, default=PaymentMethodType.CASH)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="payment_methods")
    transactions = relationship("Transaction", back_populates="payment_method")
    
    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, name='{self.name}', type='{self.type.value}')>"


class Transaction(Base):
    """Transaction model - stores income/expense records
    
    Attributes:
        id: Primary key, auto-increment
        user_id: Foreign key to users table
        category_id: Foreign key to categories table
        payment_method_id: Foreign key to payment_methods table (nullable)
        amount: Transaction amount (positive for income, stored as absolute value)
        date: Transaction date
        description: Transaction description/notes, max 500 characters
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id", ondelete="SET NULL"), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    payment_method = relationship("PaymentMethod", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, date='{self.date}', category_id={self.category_id})>"
