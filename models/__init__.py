"""SQLAlchemy models package.

Provides declarative base and exports all ORM models.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# Create declarative base for all models
Base = declarative_base()

# Import models after Base is defined to avoid circular imports
from models.user import User
from models.category import Category
from models.payment_method import PaymentMethod
from models.transaction import Transaction

__all__ = [
    "Base",
    "User",
    "Category",
    "PaymentMethod",
    "Transaction",
]


if __name__ == "__main__":
    # Self-test: verify models can be imported and tables can be created
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    print("✓ All models loaded successfully")
    print(f"✓ Tables: {list(Base.metadata.tables.keys())}")
