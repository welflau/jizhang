"""User model definition.

Represents application users with authentication credentials.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models import Base


class User(Base):
    """User account model.
    
    Attributes:
        id: Primary key
        username: Unique username (3-30 chars)
        email: Unique email address
        password_hash: Hashed password (never store plaintext)
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    
    Relationships:
        categories: User's custom categories
        payment_methods: User's payment methods
        transactions: User's transaction records
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships (use back_populates for explicit bidirectional refs)
    categories = relationship(
        "Category",
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
    transactions = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from models import Base
    
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    print(f"✓ User table created: {User.__tablename__}")
    print(f"✓ Columns: {[c.name for c in User.__table__.columns]}")
