from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bills = relationship("Bill", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False)  # income or expense
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="categories")
    bills = relationship("Bill", back_populates="category")

    __table_args__ = (
        Index('idx_category_user_type', 'user_id', 'type'),
        Index('idx_category_user_name', 'user_id', 'name'),
    )


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(String(20), nullable=False, index=True)  # income or expense
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    description = Column(String(500))
    bill_date = Column(DateTime, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="bills")
    category = relationship("Category", back_populates="bills")

    __table_args__ = (
        Index('idx_bill_user_date', 'user_id', 'bill_date'),
        Index('idx_bill_user_type', 'user_id', 'type'),
        Index('idx_bill_user_category', 'user_id', 'category_id'),
        Index('idx_bill_user_amount', 'user_id', 'amount'),
        Index('idx_bill_date_type', 'bill_date', 'type'),
        Index('idx_bill_composite', 'user_id', 'bill_date', 'type', 'category_id'),
    )