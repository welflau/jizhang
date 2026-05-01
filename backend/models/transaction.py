from datetime import datetime
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field, validator
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionCategory(str, Enum):
    # 收入类别
    SALARY = "salary"
    BONUS = "bonus"
    INVESTMENT = "investment"
    OTHER_INCOME = "other_income"
    
    # 支出类别
    FOOD = "food"
    TRANSPORT = "transport"
    HOUSING = "housing"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    OTHER_EXPENSE = "other_expense"


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class TransactionBase(BaseModel):
    type: TransactionType
    category: TransactionCategory
    amount: float = Field(..., gt=0, description="金额必须大于0")
    description: Optional[str] = Field(None, max_length=500)
    date: datetime
    tags: Optional[list[str]] = Field(default_factory=list)

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("金额必须大于0")
        # 保留两位小数
        return round(v, 2)

    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError("标签数量不能超过10个")
        return v

    @validator('description')
    def validate_description(cls, v):
        if v and len(v.strip()) == 0:
            return None
        return v

    class Config:
        use_enum_values = True


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    type: Optional[TransactionType] = None
    category: Optional[TransactionCategory] = None
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=500)
    date: Optional[datetime] = None
    tags: Optional[list[str]] = None

    @validator('amount')
    def validate_amount(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError("金额必须大于0")
            return round(v, 2)
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v is not None and len(v) > 10:
            raise ValueError("标签数量不能超过10个")
        return v

    class Config:
        use_enum_values = True


class TransactionInDB(TransactionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda v: v.isoformat()}


class TransactionResponse(BaseModel):
    id: str = Field(..., alias="_id")
    type: str
    category: str
    amount: float
    description: Optional[str]
    date: datetime
    tags: list[str]
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[TransactionResponse]


class TransactionFilter(BaseModel):
    type: Optional[TransactionType] = None
    category: Optional[TransactionCategory] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)
    tags: Optional[list[str]] = None
    search: Optional[str] = None

    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        if v is not None and 'min_amount' in values and values['min_amount'] is not None:
            if v < values['min_amount']:
                raise ValueError("最大金额不能小于最小金额")
        return v

    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v < values['start_date']:
                raise ValueError("结束日期不能早于开始日期")
        return v

    class Config:
        use_enum_values = True