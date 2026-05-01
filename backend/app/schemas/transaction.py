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
    type: TransactionType = Field(..., description="Transaction type: income or expense")
    amount: float = Field(..., gt=0, description="Transaction amount, must be greater than 0")
    category_id: int = Field(..., description="Category ID")
    date: datetime = Field(..., description="Transaction date")
    note: Optional[str] = Field(None, max_length=500, description="Transaction note")
    payment_method: PaymentMethod = Field(..., description="Payment method")

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        # Round to 2 decimal places
        return round(v, 2)

    @validator('note')
    def validate_note(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v


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

    @validator('note')
    def validate_note(cls, v):
        if v is not None and len(v.strip()) == 0:
            return None
        return v


class TransactionInDBBase(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Transaction(TransactionInDBBase):
    pass


class TransactionWithCategory(Transaction):
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    category_color: Optional[str] = None

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    total: int
    items: list[TransactionWithCategory]
    page: int
    page_size: int
    total_pages: int


class TransactionSummary(BaseModel):
    total_income: float
    total_expense: float
    balance: float
    transaction_count: int


class TransactionStatsByCategory(BaseModel):
    category_id: int
    category_name: str
    category_icon: Optional[str] = None
    category_color: Optional[str] = None
    total_amount: float
    transaction_count: int
    percentage: float


class TransactionStatsByPaymentMethod(BaseModel):
    payment_method: PaymentMethod
    total_amount: float
    transaction_count: int
    percentage: float


class TransactionMonthlyStats(BaseModel):
    year: int
    month: int
    total_income: float
    total_expense: float
    balance: float
    transaction_count: int


class TransactionDailyStats(BaseModel):
    date: str
    total_income: float
    total_expense: float
    balance: float
    transaction_count: int