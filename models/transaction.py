"""Transaction model definition.

Represents financial transactions (income/expense records).
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models import Base


class Transaction(Base):
    """Transaction record model.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        category_id: Foreign key to categories table
        payment_method_id: Foreign key to payment_methods table (nullable)
        amount: Transaction amount (positive for income, can be negative for expense)
        date: Transaction date
        description: Optional transaction description/note
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    
    Relationships:
        user: Transaction owner
        category: Transaction category
        payment_method: Payment method used
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    payment_method_id = Column(
        Integer,
        ForeignKey("payment_methods.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    date = Column(Date, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    payment_method = relationship("PaymentMethod", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, date={self.date}, category_id={self.category_id})>"


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from models import Base
    
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    print(f"✓ Transaction table created: {Transaction.__tablename__}")
    print(f"✓ Columns: {[c.name for c in Transaction.__table__.columns]}")
    print(f"✓ Foreign keys: {[fk.target_fullname for fk in Transaction.__table__.foreign_keys]}")
