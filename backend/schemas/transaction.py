from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
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
    wechat_pay = "wechat_pay"
    other = "other"


class TransactionBase(BaseModel):
    type: TransactionType
    amount: float = Field(..., gt=0, description="Transaction amount must be positive")
    category_id: int
    date: datetime
    note: Optional[str] = Field(None, max_length=500)
    payment_method: PaymentMethod

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
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
                raise ValueError('Amount must be positive')
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


class TransactionResponse(TransactionInDB):
    pass


class TransactionListResponse(BaseModel):
    total: int
    items: list[TransactionResponse]
    page: int
    page_size: int
    total_pages: int


class TransactionSummary(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    transaction_count: int


class TransactionFilter(BaseModel):
    type: Optional[TransactionType] = None
    category_id: Optional[int] = None
    payment_method: Optional[PaymentMethod] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    search: Optional[str] = None