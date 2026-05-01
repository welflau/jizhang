from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class TransactionBase(BaseModel):
    """Transaction base schema"""
    amount: Decimal = Field(..., gt=0, description="Transaction amount, must be positive")
    type: str = Field(..., description="Transaction type: income or expense")
    category_id: int = Field(..., description="Category ID")
    description: Optional[str] = Field(None, max_length=500, description="Transaction description")
    transaction_date: datetime = Field(..., description="Transaction date")

    @validator('type')
    def validate_type(cls, v):
        if v not in ['income', 'expense']:
            raise ValueError('Type must be either "income" or "expense"')
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        # Limit to 2 decimal places
        if v.as_tuple().exponent < -2:
            raise ValueError('Amount can have at most 2 decimal places')
        return v


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction"""
    pass


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction"""
    amount: Optional[Decimal] = Field(None, gt=0, description="Transaction amount")
    type: Optional[str] = Field(None, description="Transaction type: income or expense")
    category_id: Optional[int] = Field(None, description="Category ID")
    description: Optional[str] = Field(None, max_length=500, description="Transaction description")
    transaction_date: Optional[datetime] = Field(None, description="Transaction date")

    @validator('type')
    def validate_type(cls, v):
        if v is not None and v not in ['income', 'expense']:
            raise ValueError('Type must be either "income" or "expense"')
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Amount must be greater than 0')
            if v.as_tuple().exponent < -2:
                raise ValueError('Amount can have at most 2 decimal places')
        return v


class TransactionResponse(TransactionBase):
    """Schema for transaction response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class TransactionListResponse(BaseModel):
    """Schema for transaction list response with pagination"""
    total: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    transactions: list[TransactionResponse] = Field(..., description="List of transactions")


class TransactionFilter(BaseModel):
    """Schema for filtering transactions"""
    type: Optional[str] = Field(None, description="Filter by type: income or expense")
    category_id: Optional[int] = Field(None, description="Filter by category ID")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="Filter by minimum amount")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="Filter by maximum amount")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Number of items per page")

    @validator('type')
    def validate_type(cls, v):
        if v is not None and v not in ['income', 'expense']:
            raise ValueError('Type must be either "income" or "expense"')
        return v

    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v < values['start_date']:
                raise ValueError('End date must be after start date')
        return v

    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        if v is not None and 'min_amount' in values and values['min_amount'] is not None:
            if v < values['min_amount']:
                raise ValueError('Max amount must be greater than or equal to min amount')
        return v