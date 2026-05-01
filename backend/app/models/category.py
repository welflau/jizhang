from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class CategoryType(str, enum.Enum):
    income = "income"
    expense = "expense"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    type = Column(SQLEnum(CategoryType), nullable=False)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")

    # Indexes for query optimization
    __table_args__ = (
        Index('idx_category_user_id', 'user_id'),
        Index('idx_category_type', 'type'),
        Index('idx_category_user_type', 'user_id', 'type'),
        Index('idx_category_is_default', 'is_default'),
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}', user_id={self.user_id})>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "type": self.type.value if isinstance(self.type, CategoryType) else self.type,
            "icon": self.icon,
            "color": self.color,
            "is_default": self.is_default
        }