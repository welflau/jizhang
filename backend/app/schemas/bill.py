from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum


class BillType(str, Enum):
    """账单类型枚举"""
    INCOME = "income"  # 收入
    EXPENSE = "expense"  # 支出


class BillBase(BaseModel):
    """账单基础模型"""
    amount: Decimal = Field(..., gt=0, description="金额，必须大于0")
    type: BillType = Field(..., description="账单类型：收入或支出")
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
    type: Optional[BillType] = Field(None, description="账单类型")
    category_id: Optional[int] = Field(None, description="分类ID")
    description: Optional[str] = Field(None, max_length=500, description="账单描述")
    bill_date: Optional[datetime] = Field(None, description="账单日期")

    @validator('amount')
    def validate_amount(cls, v):
        if v is not None and v.as_tuple().exponent < -2:
            raise ValueError('金额最多保留两位小数')
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


class BillQueryParams(BaseModel):
    """账单查询参数模型"""
    # 时间范围
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    
    # 分类和类型
    category_ids: Optional[List[int]] = Field(None, description="分类ID列表")
    type: Optional[BillType] = Field(None, description="账单类型")
    
    # 金额范围
    min_amount: Optional[Decimal] = Field(None, ge=0, description="最小金额")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="最大金额")
    
    # 关键词搜索
    keyword: Optional[str] = Field(None, max_length=100, description="搜索关键词（描述）")
    
    # 分页参数
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    
    # 排序参数
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


class BillListResponse(BaseModel):
    """账单列表响应模型"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    items: List[BillResponse] = Field(..., description="账单列表")


class BillStatistics(BaseModel):
    """账单统计模型"""
    total_income: Decimal = Field(..., description="总收入")
    total_expense: Decimal = Field(..., description="总支出")
    balance: Decimal = Field(..., description="结余（收入-支出）")
    count: int = Field(..., description="账单总数")
    income_count: int = Field(..., description="收入账单数")
    expense_count: int = Field(..., description="支出账单数")


class CategoryStatistics(BaseModel):
    """分类统计模型"""
    category_id: int = Field(..., description="分类ID")
    category_name: str = Field(..., description="分类名称")
    total_amount: Decimal = Field(..., description="总金额")
    count: int = Field(..., description="账单数量")
    percentage: Decimal = Field(..., description="占比百分比")


class BillStatisticsResponse(BaseModel):
    """账单统计响应模型"""
    overview: BillStatistics = Field(..., description="总体统计")
    income_by_category: List[CategoryStatistics] = Field(..., description="收入分类统计")
    expense_by_category: List[CategoryStatistics] = Field(..., description="支出分类统计")


class MonthlyStatistics(BaseModel):
    """月度统计模型"""
    year: int = Field(..., description="年份")
    month: int = Field(..., description="月份")
    total_income: Decimal = Field(..., description="月度总收入")
    total_expense: Decimal = Field(..., description="月度总支出")
    balance: Decimal = Field(..., description="月度结余")
    count: int = Field(..., description="月度账单数")


class BillTrendResponse(BaseModel):
    """账单趋势响应模型"""
    monthly_data: List[MonthlyStatistics] = Field(..., description="月度数据列表")


# 数据库索引说明（在模型文件中作为注释）
"""
数据库索引设计：

1. 复合索引（推荐）：
   - idx_bill_user_date: (user_id, bill_date DESC)
     用途：用户按时间查询账单（最常用）
   
   - idx_bill_user_type_date: (user_id, type, bill_date DESC)
     用途：用户按类型和时间查询
   
   - idx_bill_user_category_date: (user_id, category_id, bill_date DESC)
     用途：用户按分类和时间查询

2. 单列索引：
   - idx_bill_amount: (amount)
     用途：金额范围查询
   
   - idx_bill_created_at: (created_at)
     用途：按创建时间排序

3. 全文索引（可选）：
   - idx_bill_description: FULLTEXT(description)
     用途：关键词搜索（MySQL 5.6+）

索引创建建议：
- 优先创建复合索引，覆盖最常用的查询场景
- 避免创建过多索引，影响写入性能
- 定期分析慢查询日志，优化索引策略
- 考虑使用 EXPLAIN 分析查询执行计划
"""