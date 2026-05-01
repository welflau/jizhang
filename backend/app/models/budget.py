from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Float, nullable=False)
    period = Column(String(7), nullable=False)  # Format: YYYY-MM
    spent = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category")

    # Indexes for performance
    __table_args__ = (
        Index('idx_user_period', 'user_id', 'period'),
        Index('idx_user_category_period', 'user_id', 'category_id', 'period', unique=True),
    )

    def to_dict(self):
        """Convert budget to dictionary with usage calculation"""
        percentage = (self.spent / self.amount * 100) if self.amount > 0 else 0
        remaining = self.amount - self.spent
        
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else "全部分类",
            "amount": round(self.amount, 2),
            "spent": round(self.spent, 2),
            "remaining": round(remaining, 2),
            "percentage": round(percentage, 2),
            "period": self.period,
            "status": self._get_status(percentage),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def _get_status(self, percentage):
        """Determine budget status based on usage percentage"""
        if percentage >= 100:
            return "exceeded"
        elif percentage >= 80:
            return "warning"
        elif percentage >= 50:
            return "normal"
        else:
            return "safe"

    def update_spent_amount(self, db):
        """Recalculate spent amount from transactions"""
        from app.models.transaction import Transaction
        
        # Parse period to get start and end dates
        year, month = map(int, self.period.split('-'))
        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1
        
        start_date = datetime(year, month, 1)
        end_date = datetime(next_year, next_month, 1)
        
        # Query transactions for this period
        query = db.query(Transaction).filter(
            Transaction.user_id == self.user_id,
            Transaction.type == "expense",
            Transaction.date >= start_date,
            Transaction.date < end_date
        )
        
        # Filter by category if specified
        if self.category_id:
            query = query.filter(Transaction.category_id == self.category_id)
        
        # Calculate total spent
        total = query.with_entities(db.func.sum(Transaction.amount)).scalar()
        self.spent = float(total) if total else 0.0
        
        return self.spent

    @staticmethod
    def validate_period(period: str) -> bool:
        """Validate period format (YYYY-MM)"""
        if not period or len(period) != 7:
            return False
        
        try:
            year, month = period.split('-')
            if len(year) != 4 or len(month) != 2:
                return False
            
            year_int = int(year)
            month_int = int(month)
            
            if year_int < 2000 or year_int > 2100:
                return False
            if month_int < 1 or month_int > 12:
                return False
            
            return True
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def validate_amount(amount: float) -> bool:
        """Validate budget amount"""
        try:
            return float(amount) > 0
        except (ValueError, TypeError):
            return False