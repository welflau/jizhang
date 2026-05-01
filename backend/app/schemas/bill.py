from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class BillType(str, Enum):
    """账单类型枚举"""
    INCOME = "income"  # 收入
    EXPENSE = "expense"  # 支出


class BillBase(BaseModel):
    """账单基础模型"""
    amount: Decimal = Field(..., gt=0, description="金额，必须大于0")
    bill_type: BillType = Field(..., description="账单类型：收入或支出")
    category_id: int = Field(..., description="分类ID")
    description: Optional[str] = Field(None, max_length=500, description="账单描述")
    bill_date: datetime = Field(..., description="账单日期")
    
    @validator('amount')
    def validate_amount(cls, v):
        """验证金额精度"""
        if v.as_tuple().exponent < -2:
            raise ValueError('金额最多保留两位小数')
        return v


class BillCreate(BillBase):
    """创建账单请求模型"""
    pass


class BillUpdate(BaseModel):
    """更新账单请求模型"""
    amount: Optional[Decimal] = Field(None, gt=0, description="金额")
    bill_type: Optional[BillType] = Field(None, description="账单类型")
    category_id: Optional[int] = Field(None, description="分类ID")
    description: Optional[str] = Field(None, max_length=500, description="账单描述")
    bill_date: Optional[datetime] = Field(None, description="账单日期")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v is not None and v.as_tuple().exponent < -2:
            raise ValueError('金额最多保留两位小数')
        return v


class BillQueryParams(BaseModel):
    """账单查询参数模型"""
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    bill_type: Optional[BillType] = Field(None, description="账单类型筛选")
    category_ids: Optional[List[int]] = Field(None, description="分类ID列表")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="最小金额")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="最大金额")
    keyword: Optional[str] = Field(None, max_length=100, description="关键词搜索（描述）")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    order_by: Optional[str] = Field("bill_date", description="排序字段")
    order_desc: bool = Field(True, description="是否降序")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """验证日期范围"""
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('结束日期不能早于开始日期')
        return v
    
    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        """验证金额范围"""
        if v and 'min_amount' in values and values['min_amount']:
            if v < values['min_amount']:
                raise ValueError('最大金额不能小于最小金额')
        return v


class BillInDB(BillBase):
    """数据库中的账单模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BillResponse(BillInDB):
    """账单响应模型"""
    category_name: Optional[str] = Field(None, description="分类名称")


class BillListResponse(BaseModel):
    """账单列表响应模型"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    items: List[BillResponse] = Field(..., description="账单列表")


class BillStatistics(BaseModel):
    """账单统计模型"""
    total_income: Decimal = Field(default=Decimal('0'), description="总收入")
    total_expense: Decimal = Field(default=Decimal('0'), description="总支出")
    balance: Decimal = Field(default=Decimal('0'), description="收支差额")
    count: int = Field(default=0, description="账单总数")
    income_count: int = Field(default=0, description="收入笔数")
    expense_count: int = Field(default=0, description="支出笔数")


class BillCategoryStatistics(BaseModel):
    """分类统计模型"""
    category_id: int = Field(..., description="分类ID")
    category_name: str = Field(..., description="分类名称")
    bill_type: BillType = Field(..., description="账单类型")
    total_amount: Decimal = Field(..., description="总金额")
    count: int = Field(..., description="账单数量")
    percentage: Decimal = Field(..., description="占比（百分比）")


class BillStatisticsResponse(BaseModel):
    """账单统计响应模型"""
    summary: BillStatistics = Field(..., description="总体统计")
    category_statistics: List[BillCategoryStatistics] = Field(..., description="分类统计")


class BillTrendItem(BaseModel):
    """账单趋势项"""
    date: str = Field(..., description="日期（格式：YYYY-MM-DD）")
    income: Decimal = Field(default=Decimal('0'), description="收入")
    expense: Decimal = Field(default=Decimal('0'), description="支出")
    balance: Decimal = Field(default=Decimal('0'), description="收支差额")


class BillTrendResponse(BaseModel):
    """账单趋势响应模型"""
    items: List[BillTrendItem] = Field(..., description="趋势数据")


class BillBatchDeleteRequest(BaseModel):
    """批量删除账单请求模型"""
    bill_ids: List[int] = Field(..., min_items=1, description="要删除的账单ID列表")


class BillImportItem(BaseModel):
    """账单导入项"""
    amount: Decimal = Field(..., gt=0)
    bill_type: BillType
    category_name: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    bill_date: datetime


class BillImportRequest(BaseModel):
    """账单导入请求模型"""
    items: List[BillImportItem] = Field(..., min_items=1, max_items=1000, description="导入的账单列表")


class BillImportResponse(BaseModel):
    """账单导入响应模型"""
    success_count: int = Field(..., description="成功导入数量")
    fail_count: int = Field(..., description="失败数量")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")