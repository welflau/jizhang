from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class BudgetBase(BaseModel):
    """预算基础模型"""
    category_id: int = Field(..., description="分类ID")
    amount: Decimal = Field(..., gt=0, description="预算金额，必须大于0")
    period: str = Field(..., description="预算周期，格式: YYYY-MM")
    
    @validator('amount')
    def validate_amount(cls, v):
        """验证金额必须大于0且最多两位小数"""
        if v <= 0:
            raise ValueError('预算金额必须大于0')
        if v.as_tuple().exponent < -2:
            raise ValueError('预算金额最多保留两位小数')
        return v
    
    @validator('period')
    def validate_period(cls, v):
        """验证周期格式为 YYYY-MM"""
        try:
            datetime.strptime(v, '%Y-%m')
        except ValueError:
            raise ValueError('预算周期格式必须为 YYYY-MM')
        return v


class BudgetCreate(BudgetBase):
    """创建预算请求模型"""
    pass


class BudgetUpdate(BaseModel):
    """更新预算请求模型"""
    category_id: Optional[int] = Field(None, description="分类ID")
    amount: Optional[Decimal] = Field(None, gt=0, description="预算金额")
    period: Optional[str] = Field(None, description="预算周期，格式: YYYY-MM")
    
    @validator('amount')
    def validate_amount(cls, v):
        """验证金额必须大于0且最多两位小数"""
        if v is not None:
            if v <= 0:
                raise ValueError('预算金额必须大于0')
            if v.as_tuple().exponent < -2:
                raise ValueError('预算金额最多保留两位小数')
        return v
    
    @validator('period')
    def validate_period(cls, v):
        """验证周期格式为 YYYY-MM"""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m')
            except ValueError:
                raise ValueError('预算周期格式必须为 YYYY-MM')
        return v


class BudgetResponse(BudgetBase):
    """预算响应模型"""
    id: int
    user_id: int
    spent: Decimal = Field(default=Decimal('0'), description="已使用金额")
    percentage: float = Field(default=0.0, description="使用百分比")
    remaining: Decimal = Field(default=Decimal('0'), description="剩余金额")
    status: str = Field(default="normal", description="预算状态: normal, warning, exceeded")
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
    """预算列表响应模型"""
    total: int = Field(..., description="总记录数")
    items: list[BudgetResponse] = Field(..., description="预算列表")


class BudgetQuery(BaseModel):
    """预算查询参数模型"""
    period: Optional[str] = Field(None, description="筛选周期，格式: YYYY-MM")
    category_id: Optional[int] = Field(None, description="筛选分类ID")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    
    @validator('period')
    def validate_period(cls, v):
        """验证周期格式为 YYYY-MM"""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m')
            except ValueError:
                raise ValueError('预算周期格式必须为 YYYY-MM')
        return v