"""Category model definition.

Represents income/expense categories for transaction classification.
"""
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from models import Base


class CategoryType(enum.Enum):
    """Category type enumeration."""
    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):
    """Transaction category model.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        name: Category name (e.g., 'Salary', 'Food', 'Transport')
        type: Category type (income/expense)
        icon: Icon identifier (e.g., 'wallet', 'food', 'car')
        color: Hex color code for UI display (e.g., '#FF5733')
    
    Relationships:
        user: Category owner
        transactions: Transactions under this category
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name = Column(String(50), nullable=False)
    type = Column(Enum(CategoryType), nullable=False, index=True)
    icon = Column(String(50), nullable=True, default="default")
    color = Column(String(7), nullable=True, default="#6C757D")  # Bootstrap secondary color

    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship(
        "Transaction",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type={self.type.value})>"


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from models import Base
    
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    print(f"✓ Category table created: {Category.__tablename__}")
    print(f"✓ Columns: {[c.name for c in Category.__table__.columns]}")
    print(f"✓ Enum values: {[t.value for t in CategoryType]}")
