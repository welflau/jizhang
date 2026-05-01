from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class BudgetBase(BaseModel):
    category_id: int = Field(..., description="分类ID")
    amount: Decimal = Field(..., gt=0, description="预算金额，必须大于0")
    period: str = Field(..., description="预算周期，格式：YYYY-MM")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('预算金额必须大于0')
        # 保留两位小数
        return round(v, 2)
    
    @validator('period')
    def validate_period(cls, v):
        # 验证格式 YYYY-MM
        try:
            datetime.strptime(v, '%Y-%m')
        except ValueError:
            raise ValueError('预算周期格式必须为 YYYY-MM')
        return v


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    category_id: Optional[int] = Field(None, description="分类ID")
    amount: Optional[Decimal] = Field(None, gt=0, description="预算金额")
    period: Optional[str] = Field(None, description="预算周期，格式：YYYY-MM")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('预算金额必须大于0')
            return round(v, 2)
        return v
    
    @validator('period')
    def validate_period(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m')
            except ValueError:
                raise ValueError('预算周期格式必须为 YYYY-MM')
        return v


class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    spent: Decimal = Field(default=0, description="已使用金额")
    percentage: float = Field(default=0, description="使用百分比")
    remaining: Decimal = Field(default=0, description="剩余金额")
    category_name: Optional[str] = Field(None, description="分类名称")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class BudgetListResponse(BaseModel):
    total: int
    budgets: list[BudgetResponse]
