"""Payment method model definition.

Represents payment methods (cash, credit card, debit card, etc.).
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models import Base


class PaymentMethod(Base):
    """Payment method model.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table
        name: Payment method name (e.g., 'Cash', 'Visa Card', 'Alipay')
        type: Payment type (e.g., 'cash', 'credit_card', 'debit_card', 'e_wallet')
    
    Relationships:
        user: Payment method owner
        transactions: Transactions using this payment method
    """
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False, default="cash")  # cash, credit_card, debit_card, e_wallet, bank_transfer

    # Relationships
    user = relationship("User", back_populates="payment_methods")
    transactions = relationship(
        "Transaction",
        back_populates="payment_method",
        lazy="select"
    )

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, name='{self.name}', type='{self.type}')>"


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from models import Base
    
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    print(f"✓ PaymentMethod table created: {PaymentMethod.__tablename__}")
    print(f"✓ Columns: {[c.name for c in PaymentMethod.__table__.columns]}")
