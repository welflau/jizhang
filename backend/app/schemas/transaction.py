from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class PaymentMethod(str, Enum):
    cash = "cash"
    credit_card = "credit_card"
    debit_card = "debit_card"
    bank_transfer = "bank_transfer"
    alipay = "alipay"
    wechat = "wechat"
    other = "other"


class TransactionBase(BaseModel):
    type: TransactionType
    amount: float = Field(..., gt=0, description="Transaction amount must be greater than 0")
    category_id: int
    date: datetime
    note: Optional[str] = Field(None, max_length=500)
    payment_method: PaymentMethod

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        # Round to 2 decimal places
        return round(v, 2)


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    type: Optional[TransactionType] = None
    amount: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    date: Optional[datetime] = None
    note: Optional[str] = Field(None, max_length=500)
    payment_method: Optional[PaymentMethod] = None

    @validator('amount')
    def validate_amount(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Amount must be greater than 0')
            return round(v, 2)
        return v


class TransactionInDB(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class Transaction(TransactionInDB):
    pass


class TransactionResponse(TransactionInDB):
    category_name: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True


class TransactionListResponse(BaseModel):
    total: int
    items: list[TransactionResponse]
    page: int
    page_size: int
    total_pages: int


class TransactionFilter(BaseModel):
    type: Optional[TransactionType] = None
    category_id: Optional[int] = None
    payment_method: Optional[PaymentMethod] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)
    search: Optional[str] = Field(None, max_length=100)

    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        if v is not None and 'min_amount' in values and values['min_amount'] is not None:
            if v < values['min_amount']:
                raise ValueError('max_amount must be greater than or equal to min_amount')
        return v


class TransactionStatistics(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    transaction_count: int
    avg_income: float
    avg_expense: float
    period_start: datetime
    period_end: datetime


class CategoryStatistics(BaseModel):
    category_id: int
    category_name: str
    total_amount: float
    transaction_count: int
    percentage: float


class MonthlyStatistics(BaseModel):
    year: int
    month: int
    total_income: float
    total_expense: float
    balance: float
    transaction_count: int


class TransactionSummary(BaseModel):
    statistics: TransactionStatistics
    category_breakdown: list[CategoryStatistics]
    monthly_trend: list[MonthlyStatistics]