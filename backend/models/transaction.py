from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class TransactionBase(BaseModel):
    """Base transaction schema with common fields."""
    type: Literal["income", "expense"] = Field(description="Transaction type: income or expense")
    amount: float = Field(gt=0, description="Transaction amount, must be positive")
    category_id: int = Field(ge=1, description="Category ID reference")
    date: datetime = Field(description="Transaction date")
    note: Optional[str] = Field(None, max_length=500, description="Optional note")
    payment_method: Optional[str] = Field(None, max_length=50, description="Payment method (cash, card, etc.)")


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""
    pass


class TransactionUpdate(BaseModel):
    """Schema for updating an existing transaction (all fields optional)."""
    type: Optional[Literal["income", "expense"]] = None
    amount: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, ge=1)
    date: Optional[datetime] = None
    note: Optional[str] = Field(None, max_length=500)
    payment_method: Optional[str] = Field(None, max_length=50)


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
