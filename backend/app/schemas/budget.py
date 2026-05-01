from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class BudgetBase(BaseModel):
    """预算基础模型"""
    category_id: int = Field(..., description="分类ID")
    amount: float = Field(..., gt=0, description="预算金额，必须大于0")
    period: str = Field(..., description="预算周期，格式：YYYY-MM")
    
    @field_validator('period')
    @classmethod
    def validate_period(cls, v: str) -> str:
        """验证预算周期格式"""
        if not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', v):
            raise ValueError('预算周期格式必须为 YYYY-MM，例如：2024-01')
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """验证金额精度"""
        if round(v, 2) != v:
            raise ValueError('金额最多保留两位小数')
        return v


class BudgetCreate(BudgetBase):
    """创建预算请求模型"""
    pass


class BudgetUpdate(BaseModel):
    """更新预算请求模型"""
    category_id: Optional[int] = Field(None, description="分类ID")
    amount: Optional[float] = Field(None, gt=0, description="预算金额，必须大于0")
    period: Optional[str] = Field(None, description="预算周期，格式：YYYY-MM")
    
    @field_validator('period')
    @classmethod
    def validate_period(cls, v: Optional[str]) -> Optional[str]:
        """验证预算周期格式"""
        if v is not None and not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', v):
            raise ValueError('预算周期格式必须为 YYYY-MM，例如：2024-01')
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Optional[float]) -> Optional[float]:
        """验证金额精度"""
        if v is not None and round(v, 2) != v:
            raise ValueError('金额最多保留两位小数')
        return v


class BudgetResponse(BudgetBase):
    """预算响应模型"""
    id: int
    user_id: int
    spent: float = Field(default=0.0, description="已使用金额")
    remaining: float = Field(default=0.0, description="剩余金额")
    percentage: float = Field(default=0.0, ge=0, le=100, description="使用百分比")
    is_exceeded: bool = Field(default=False, description="是否超支")
    category_name: Optional[str] = Field(None, description="分类名称")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BudgetListResponse(BaseModel):
    """预算列表响应模型"""
    total: int = Field(..., description="总记录数")
    items: list[BudgetResponse] = Field(..., description="预算列表")


class BudgetQuery(BaseModel):
    """预算查询参数模型"""
    period: Optional[str] = Field(None, description="预算周期筛选，格式：YYYY-MM")
    category_id: Optional[int] = Field(None, description="分类ID筛选")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    
    @field_validator('period')
    @classmethod
    def validate_period(cls, v: Optional[str]) -> Optional[str]:
        """验证预算周期格式"""
        if v is not None and not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', v):
            raise ValueError('预算周期格式必须为 YYYY-MM，例如：2024-01')
        return v


class BudgetSummary(BaseModel):
    """预算汇总模型"""
    period: str = Field(..., description="预算周期")
    total_budget: float = Field(..., description="总预算")
    total_spent: float = Field(..., description="总支出")
    total_remaining: float = Field(..., description="总剩余")
    overall_percentage: float = Field(..., ge=0, description="总体使用百分比")
    exceeded_count: int = Field(..., ge=0, description="超支预算数量")
    budgets: list[BudgetResponse] = Field(..., description="预算明细列表")
