"""
Statistics API Schema Definitions
统计数据聚合 API 接口规范
"""

from datetime import date, datetime
from typing import List, Optional, Literal
from decimal import Decimal
from pydantic import BaseModel, Field, validator


# ==================== 收支趋势查询接口 ====================

class TrendQueryRequest(BaseModel):
    """收支趋势查询请求"""
    dimension: Literal['day', 'week', 'month'] = Field(
        ...,
        description="统计维度: day-按天, week-按周, month-按月"
    )
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    type: Optional[Literal['income', 'expense', 'both']] = Field(
        'both',
        description="统计类型: income-收入, expense-支出, both-全部"
    )

    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期不能早于开始日期')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "dimension": "month",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "type": "both"
            }
        }


class TrendDataPoint(BaseModel):
    """趋势数据点"""
    period: str = Field(..., description="时间周期标识（如：2024-01, 2024-W01, 2024-01-01）")
    income: Decimal = Field(..., description="收入金额")
    expense: Decimal = Field(..., description="支出金额")
    balance: Decimal = Field(..., description="结余（收入-支出）")
    transaction_count: int = Field(..., description="交易笔数")

    class Config:
        json_schema_extra = {
            "example": {
                "period": "2024-01",
                "income": "15000.00",
                "expense": "8500.00",
                "balance": "6500.00",
                "transaction_count": 45
            }
        }


class TrendQueryResponse(BaseModel):
    """收支趋势查询响应"""
    dimension: str = Field(..., description="统计维度")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    data: List[TrendDataPoint] = Field(..., description="趋势数据列表")
    total_income: Decimal = Field(..., description="总收入")
    total_expense: Decimal = Field(..., description="总支出")
    total_balance: Decimal = Field(..., description="总结余")
    avg_income: Decimal = Field(..., description="平均收入")
    avg_expense: Decimal = Field(..., description="平均支出")


# ==================== 分类占比统计接口 ====================

class CategoryRatioRequest(BaseModel):
    """分类占比统计请求"""
    type: Literal['income', 'expense'] = Field(..., description="统计类型: income-收入, expense-支出")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    top_n: Optional[int] = Field(10, ge=1, le=50, description="返回前N个分类，默认10")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期不能早于开始日期')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "type": "expense",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "top_n": 10
            }
        }


class CategoryRatioItem(BaseModel):
    """分类占比数据项"""
    category_id: int = Field(..., description="分类ID")
    category_name: str = Field(..., description="分类名称")
    amount: Decimal = Field(..., description="金额")
    percentage: float = Field(..., ge=0, le=100, description="占比百分比")
    transaction_count: int = Field(..., description="交易笔数")
    avg_amount: Decimal = Field(..., description="平均金额")

    class Config:
        json_schema_extra = {
            "example": {
                "category_id": 1,
                "category_name": "餐饮",
                "amount": "2500.00",
                "percentage": 35.5,
                "transaction_count": 28,
                "avg_amount": "89.29"
            }
        }


class CategoryRatioResponse(BaseModel):
    """分类占比统计响应"""
    type: str = Field(..., description="统计类型")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    total_amount: Decimal = Field(..., description="总金额")
    categories: List[CategoryRatioItem] = Field(..., description="分类占比列表")
    other_amount: Decimal = Field(..., description="其他分类总金额")
    other_percentage: float = Field(..., description="其他分类占比")


# ==================== 月度收支对比接口 ====================

class MonthlyComparisonRequest(BaseModel):
    """月度收支对比请求"""
    year: int = Field(..., ge=2000, le=2100, description="年份")
    months: Optional[List[int]] = Field(
        None,
        description="指定月份列表（1-12），不指定则返回全年12个月"
    )

    @validator('months')
    def validate_months(cls, v):
        if v is not None:
            if not all(1 <= m <= 12 for m in v):
                raise ValueError('月份必须在1-12之间')
            if len(v) != len(set(v)):
                raise ValueError('月份不能重复')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2024,
                "months": [1, 2, 3, 4, 5, 6]
            }
        }


class MonthlyComparisonItem(BaseModel):
    """月度对比数据项"""
    month: int = Field(..., ge=1, le=12, description="月份")
    income: Decimal = Field(..., description="收入")
    expense: Decimal = Field(..., description="支出")
    balance: Decimal = Field(..., description="结余")
    income_growth_rate: Optional[float] = Field(None, description="收入环比增长率（%）")
    expense_growth_rate: Optional[float] = Field(None, description="支出环比增长率（%）")
    savings_rate: float = Field(..., description="储蓄率（%）= (收入-支出)/收入*100")

    class Config:
        json_schema_extra = {
            "example": {
                "month": 1,
                "income": "15000.00",
                "expense": "8500.00",
                "balance": "6500.00",
                "income_growth_rate": 5.2,
                "expense_growth_rate": -3.1,
                "savings_rate": 43.33
            }
        }


class MonthlyComparisonResponse(BaseModel):
    """月度收支对比响应"""
    year: int = Field(..., description="年份")
    data: List[MonthlyComparisonItem] = Field(..., description="月度对比数据")
    total_income: Decimal = Field(..., description="总收入")
    total_expense: Decimal = Field(..., description="总支出")
    total_balance: Decimal = Field(..., description="总结余")
    avg_monthly_income: Decimal = Field(..., description="月均收入")
    avg_monthly_expense: Decimal = Field(..., description="月均支出")
    avg_savings_rate: float = Field(..., description="平均储蓄率（%）")
    best_month: Optional[int] = Field(None, description="结余最多的月份")
    worst_month: Optional[int] = Field(None, description="结余最少的月份")


# ==================== 年度统计总览接口 ====================

class YearlyOverviewRequest(BaseModel):
    """年度统计总览请求"""
    year: int = Field(..., ge=2000, le=2100, description="年份")

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2024
            }
        }


class YearlyTopCategory(BaseModel):
    """年度热门分类"""
    category_id: int = Field(..., description="分类ID")
    category_name: str = Field(..., description="分类名称")
    amount: Decimal = Field(..., description="金额")
    transaction_count: int = Field(..., description="交易笔数")


class YearlyOverviewResponse(BaseModel):
    """年度统计总览响应"""
    year: int = Field(..., description="年份")
    total_income: Decimal = Field(..., description="年度总收入")
    total_expense: Decimal = Field(..., description="年度总支出")
    total_balance: Decimal = Field(..., description="年度总结余")
    total_transactions: int = Field(..., description="总交易笔数")
    
    # 月度统计
    avg_monthly_income: Decimal = Field(..., description="月均收入")
    avg_monthly_expense: Decimal = Field(..., description="月均支出")
    max_monthly_income: Decimal = Field(..., description="最高月收入")
    max_monthly_expense: Decimal = Field(..., description="最高月支出")
    
    # 分类统计
    top_expense_categories: List[YearlyTopCategory] = Field(..., description="支出前5分类")
    top_income_categories: List[YearlyTopCategory] = Field(..., description="收入前5分类")
    
    # 趋势指标
    income_growth_rate: Optional[float] = Field(None, description="相比去年收入增长率（%）")
    expense_growth_rate: Optional[float] = Field(None, description="相比去年支出增长率（%）")
    avg_savings_rate: float = Field(..., description="年度平均储蓄率（%）")
    
    # 交易统计
    avg_transaction_amount: Decimal = Field(..., description="平均交易金额")
    max_single_income: Decimal = Field(..., description="最大单笔收入")
    max_single_expense: Decimal = Field(..., description="最大单笔支出")

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2024,
                "total_income": "180000.00",
                "total_expense": "102000.00",
                "total_balance": "78000.00",
                "total_transactions": 540,
                "avg_monthly_income": "15000.00",
                "avg_monthly_expense": "8500.00",
                "max_monthly_income": "18000.00",
                "max_monthly_expense": "12000.00",
                "top_expense_categories": [],
                "top_income_categories": [],
                "income_growth_rate": 8.5,
                "expense_growth_rate": 3.2,
                "avg_savings_rate": 43.33,
                "avg_transaction_amount": "333.33",
                "max_single_income": "5000.00",
                "max_single_expense": "3000.00"
            }
        }


# ==================== 关键指标查询接口 ====================

class KeyMetricsRequest(BaseModel):
    """关键指标查询请求"""
    year: int = Field(..., ge=2000, le=2100, description="年份")
    month: int = Field(..., ge=1, le=12, description="月份")

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2024,
                "month": 1
            }
        }


class KeyMetricsResponse(BaseModel):
    """关键指标查询响应"""
    year: int = Field(..., description="年份")
    month: int = Field(..., description="月份")
    
    # 本月核心指标
    current_month_income: Decimal = Field(..., description="本月总收入")
    current_month_expense: Decimal = Field(..., description="本月总支出")
    current_month_balance: Decimal = Field(..., description="本月结余")
    current_month_transactions: int = Field(..., description="本月交易笔数")
    
    # 环比数据
    last_month_income: Optional[Decimal] = Field(None, description="上月总收入")
    last_month_expense: Optional[Decimal] = Field(None, description="上月总支出")
    last_month_balance: Optional[Decimal] = Field(None, description="上月结余")
    income_mom_rate: Optional[float] = Field(None, description="收入环比增长率（%）")
    expense_mom_rate: Optional[float] = Field(None, description="支出环比增长率（%）")
    
    # 同比数据
    last_year_income: Optional[Decimal] = Field(None, description="去年同期收入")
    last_year_expense: Optional[Decimal] = Field(None, description="去年同期支出")
    income_yoy_rate: Optional[float] = Field(None, description="收入同比增长率（%）")
    expense_yoy_rate: Optional[float] = Field(None, description="支出同比增长率（%）")
    
    # 年度累计
    ytd_income: Decimal = Field(..., description="年初至今累计收入")
    ytd_expense: Decimal = Field(..., description="年初至今累计支出")
    ytd_balance: Decimal = Field(..., description="年初至今累计结余")
    
    # 其他指标
    savings_rate: float = Field(..., description="本月储蓄率（%）")
    daily_avg_expense: Decimal = Field(..., description="日均支出")
    budget_usage_rate: Optional[float] = Field(None, description="预算使用率（%）")

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2024,
                "month": 1,
                "current_month_income": "15000.00",
                "current_month_expense": "8500.00",
                "current_month_balance": "6500.00",
                "current_month_transactions": 45,
                "last_month_income": "14000.00",
                "last_month_expense": "9000.00",
                "last_month_balance": "5000.00",
                "income_mom_rate": 7.14,
                "expense_mom_rate": -5.56,
                "last_year_income": "13500.00",
                "last_year_expense": "8000.00",
                "income_yoy_rate": 11.11,
                "expense_yoy_rate": 6.25,
                "ytd_income": "15000.00",
                "ytd_expense": "8500.00",
                "ytd_balance": "6500.00",
                "savings_rate": 43.33,
                "daily_avg_expense": "274.19",
                "budget_usage_rate": 85.0
            }
        }


# ==================== 通用响应模型 ====================

class StatisticsErrorResponse(BaseModel):
    """统计接口错误响应"""
    error_code: str = Field(..., description="错误码")
    message: str = Field(..., description="错误信息")
    details: Optional[dict] = Field(None, description="详细错误信息")

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "INVALID_DATE_RANGE",
                "message": "日期范围无效",
                "details": {
                    "start_date": "2024-01-01",
                    "end_date": "2023-12-31"
                }
            }
        }


# ==================== 错误码定义 ====================

class StatisticsErrorCode:
    """统计接口错误码"""
    
    # 参数错误 (4000-4099)
    INVALID_DIMENSION = "STATS_4000"  # 无效的统计维度
    INVALID_DATE_RANGE = "STATS_4001"  # 无效的日期范围
    INVALID_TYPE = "STATS_4002"  # 无效的统计类型
    INVALID_YEAR = "STATS_4003"  # 无效的年份
    INVALID_MONTH = "STATS_4004"  # 无效的月份
    INVALID_TOP_N = "STATS_4005"  # 无效的TOP N参数
    
    # 数据错误 (4100-4199)
    NO_DATA_FOUND = "STATS_4100"  # 未找到数据
    INSUFFICIENT_DATA = "STATS_4101"  # 数据不足
    DATA_CALCULATION_ERROR = "STATS_4102"  # 数据计算错误
    
    # 业务错误 (4200-4299)
    DATE_RANGE_TOO_LARGE = "STATS_4200"  # 日期范围过大
    FUTURE_DATE_NOT_ALLOWED = "STATS_4201"  # 不允许查询未来日期
    
    # 系统错误 (5000-5099)
    DATABASE_ERROR = "STATS_5000"  # 数据库错误
    CALCULATION_TIMEOUT = "STATS_5001"  # 计算超时
    INTERNAL_ERROR = "STATS_5999"  # 内部错误


# ==================== API 文档说明 ====================

"""
API 文档说明
============

1. 收支趋势查询接口
   - 路径: POST /api/statistics/trend
   - 请求体: TrendQueryRequest
   - 响应: TrendQueryResponse
   - 说明: 支持按天/周/月维度查询收支趋势，返回时间序列数据

2. 分类占比统计接口
   - 路径: POST /api/statistics/category-ratio
   - 请求体: CategoryRatioRequest
   - 响应: CategoryRatioResponse
   - 说明: 统计指定时间范围内各分类的金额占比，支持收入/支出分别统计

3. 月度收支对比接口
   - 路径: POST /api/statistics/monthly-comparison
   - 请求体: MonthlyComparisonRequest
   - 响应: MonthlyComparisonResponse
   - 说明: 对比指定年份各月的收支情况，包含环比增长率和储蓄率

4. 年度统计总览接口
   - 路径: POST /api/statistics/yearly-overview
   - 请求体: YearlyOverviewRequest
   - 响应: YearlyOverviewResponse
   - 说明: 提供年度全面的统计数据，包括总览、趋势、热门分类等

5. 关键指标查询接口
   - 路径: POST /api/statistics/key-metrics
   - 请求体: KeyMetricsRequest
   - 响应: KeyMetricsResponse
   - 说明: 查询指定月份的关键财务指标，包含环比、同比、年度累计数据

通用说明:
- 所有金额字段使用 Decimal 类型，保证精度
- 所有日期字段使用 date 类型（YYYY-MM-DD格式）
- 百分比字段使用 float 类型，范围 0-100
- 错误响应统一使用 StatisticsErrorResponse 格式
- 所有接口需要用户认证（JWT Token）
- 查询结果基于用户维度，只返回当前用户的数据

性能建议:
- 日期范围建议不超过1年，避免数据量过大
- 使用缓存机制提升查询性能
- 大数据量查询考虑异步处理
- 定期预计算常用统计指标

数据安全:
- 所有查询需验证用户权限
- 敏感数据需脱敏处理
- 记录查询日志用于审计
- 防止SQL注入和数据泄露
"""
