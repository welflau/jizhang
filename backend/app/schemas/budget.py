from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class BudgetBase(BaseModel):
    category_id: int = Field(..., description="分类ID")
    amount: Decimal = Field(..., gt=0, description="预算金额，必须大于0")
    period: str = Field(..., description="预算周期，格式：YYYY-MM")
    
    @validator('period')
    def validate_period(cls, v):
        """验证预算周期格式"""
        if not v:
            raise ValueError('预算周期不能为空')
        
        # 验证格式 YYYY-MM
        parts = v.split('-')
        if len(parts) != 2:
            raise ValueError('预算周期格式必须为 YYYY-MM')
        
        try:
            year = int(parts[0])
            month = int(parts[1])
            
            if year < 2000 or year > 2100:
                raise ValueError('年份必须在 2000-2100 之间')
            
            if month < 1 or month > 12:
                raise ValueError('月份必须在 1-12 之间')
            
            # 格式化为标准格式（补零）
            return f"{year:04d}-{month:02d}"
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError('预算周期格式必须为 YYYY-MM')
            raise e
    
    @validator('amount')
    def validate_amount(cls, v):
        """验证金额精度"""
        if v <= 0:
            raise ValueError('预算金额必须大于0')
        
        # 限制小数位数为2位
        if v.as_tuple().exponent < -2:
            raise ValueError('金额最多保留2位小数')
        
        return v


class BudgetCreate(BudgetBase):
    """创建预算的请求模型"""
    pass


class BudgetUpdate(BaseModel):
    """更新预算的请求模型"""
    category_id: Optional[int] = Field(None, description="分类ID")
    amount: Optional[Decimal] = Field(None, gt=0, description="预算金额，必须大于0")
    period: Optional[str] = Field(None, description="预算周期，格式：YYYY-MM")
    
    @validator('period')
    def validate_period(cls, v):
        """验证预算周期格式"""
        if v is None:
            return v
        
        # 验证格式 YYYY-MM
        parts = v.split('-')
        if len(parts) != 2:
            raise ValueError('预算周期格式必须为 YYYY-MM')
        
        try:
            year = int(parts[0])
            month = int(parts[1])
            
            if year < 2000 or year > 2100:
                raise ValueError('年份必须在 2000-2100 之间')
            
            if month < 1 or month > 12:
                raise ValueError('月份必须在 1-12 之间')
            
            # 格式化为标准格式（补零）
            return f"{year:04d}-{month:02d}"
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError('预算周期格式必须为 YYYY-MM')
            raise e
    
    @validator('amount')
    def validate_amount(cls, v):
        """验证金额精度"""
        if v is not None:
            if v <= 0:
                raise ValueError('预算金额必须大于0')
            
            # 限制小数位数为2位
            if v.as_tuple().exponent < -2:
                raise ValueError('金额最多保留2位小数')
        
        return v


class BudgetResponse(BudgetBase):
    """预算响应模型"""
    id: int
    user_id: int
    spent: Decimal = Field(default=Decimal('0'), description="已使用金额")
    remaining: Decimal = Field(default=Decimal('0'), description="剩余金额")
    percentage: float = Field(default=0.0, description="使用百分比")
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
    budgets: list[BudgetResponse] = Field(..., description="预算列表")
    
    class Config:
        from_attributes = True


class BudgetProgressResponse(BaseModel):
    """预算进度响应模型"""
    budget_id: int
    category_id: int
    category_name: str
    period: str
    amount: Decimal
    spent: Decimal
    remaining: Decimal
    percentage: float
    status: str = Field(..., description="预算状态：normal(正常), warning(警告), exceeded(超支)")
    
    @validator('status', pre=True, always=True)
    def determine_status(cls, v, values):
        """根据使用百分比确定预算状态"""
        if 'percentage' in values:
            percentage = values['percentage']
            if percentage >= 100:
                return 'exceeded'
            elif percentage >= 80:
                return 'warning'
            else:
                return 'normal'
        return 'normal'
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }
