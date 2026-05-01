# 统计数据聚合 API 接口规范

## 概述

本文档定义了记账应用统计数据聚合相关的 API 接口规范，包括收支趋势、分类占比、月度对比、年度总览和关键指标等统计功能。

**基础路径**: `/api/v1/statistics`

**通用请求头**:
```
Content-Type: application/json
Authorization: Bearer {access_token}
```

**通用响应格式**:
```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "timestamp": 1704067200000
}
```

## 1. 收支趋势查询接口

### 1.1 接口信息

- **路径**: `/api/v1/statistics/trend`
- **方法**: `GET`
- **描述**: 查询指定时间范围内的收支趋势数据，支持按日、周、月维度聚合

### 1.2 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| start_date | string | 是 | 开始日期 (YYYY-MM-DD) | 2024-01-01 |
| end_date | string | 是 | 结束日期 (YYYY-MM-DD) | 2024-01-31 |
| dimension | string | 是 | 聚合维度: day/week/month | day |
| account_id | integer | 否 | 账户ID，不传则查询所有账户 | 1 |
| category_id | integer | 否 | 分类ID，不传则查询所有分类 | 5 |

### 1.3 请求示例

```
GET /api/v1/statistics/trend?start_date=2024-01-01&end_date=2024-01-31&dimension=day
```

### 1.4 响应数据

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "dimension": "day",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "items": [
      {
        "date": "2024-01-01",
        "income": 5000.00,
        "expense": 1200.50,
        "balance": 3799.50,
        "transaction_count": 15
      },
      {
        "date": "2024-01-02",
        "income": 0.00,
        "expense": 850.00,
        "balance": -850.00,
        "transaction_count": 8
      }
    ],
    "summary": {
      "total_income": 15000.00,
      "total_expense": 8500.00,
      "net_balance": 6500.00,
      "total_transaction_count": 156
    }
  },
  "timestamp": 1704067200000
}
```

### 1.5 字段说明

- `dimension`: 实际使用的聚合维度
- `items`: 趋势数据数组
  - `date`: 日期标识（day: YYYY-MM-DD, week: YYYY-Www, month: YYYY-MM）
  - `income`: 收入金额
  - `expense`: 支出金额
  - `balance`: 净收支（收入-支出）
  - `transaction_count`: 交易笔数
- `summary`: 汇总数据

## 2. 分类占比统计接口

### 2.1 接口信息

- **路径**: `/api/v1/statistics/category-distribution`
- **方法**: `GET`
- **描述**: 统计指定时间范围内各分类的收支占比

### 2.2 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| start_date | string | 是 | 开始日期 (YYYY-MM-DD) | 2024-01-01 |
| end_date | string | 是 | 结束日期 (YYYY-MM-DD) | 2024-01-31 |
| type | string | 是 | 类型: income/expense | expense |
| account_id | integer | 否 | 账户ID | 1 |
| top_n | integer | 否 | 返回前N个分类，默认10 | 10 |

### 2.3 请求示例

```
GET /api/v1/statistics/category-distribution?start_date=2024-01-01&end_date=2024-01-31&type=expense&top_n=5
```

### 2.4 响应数据

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "type": "expense",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "total_amount": 8500.00,
    "categories": [
      {
        "category_id": 1,
        "category_name": "餐饮",
        "category_icon": "food",
        "amount": 3200.00,
        "percentage": 37.65,
        "transaction_count": 45,
        "avg_amount": 71.11
      },
      {
        "category_id": 2,
        "category_name": "交通",
        "category_icon": "transport",
        "amount": 1500.00,
        "percentage": 17.65,
        "transaction_count": 30,
        "avg_amount": 50.00
      },
      {
        "category_id": 3,
        "category_name": "购物",
        "category_icon": "shopping",
        "amount": 2000.00,
        "percentage": 23.53,
        "transaction_count": 12,
        "avg_amount": 166.67
      },
      {
        "category_id": 4,
        "category_name": "娱乐",
        "category_icon": "entertainment",
        "amount": 1200.00,
        "percentage": 14.12,
        "transaction_count": 8,
        "avg_amount": 150.00
      },
      {
        "category_id": 0,
        "category_name": "其他",
        "category_icon": "other",
        "amount": 600.00,
        "percentage": 7.05,
        "transaction_count": 10,
        "avg_amount": 60.00
      }
    ]
  },
  "timestamp": 1704067200000
}
```

### 2.5 字段说明

- `total_amount`: 总金额
- `categories`: 分类统计数组
  - `amount`: 该分类总金额
  - `percentage`: 占比百分比
  - `transaction_count`: 交易笔数
  - `avg_amount`: 平均金额
- 当请求 `top_n` 时，其余分类合并为"其他"（category_id=0）

## 3. 月度收支对比接口

### 3.1 接口信息

- **路径**: `/api/v1/statistics/monthly-comparison`
- **方法**: `GET`
- **描述**: 对比多个月份的收支情况

### 3.2 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| start_month | string | 是 | 开始月份 (YYYY-MM) | 2024-01 |
| end_month | string | 是 | 结束月份 (YYYY-MM) | 2024-06 |
| account_id | integer | 否 | 账户ID | 1 |

### 3.3 请求示例

```
GET /api/v1/statistics/monthly-comparison?start_month=2024-01&end_month=2024-06
```

### 3.4 响应数据

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "start_month": "2024-01",
    "end_month": "2024-06",
    "months": [
      {
        "month": "2024-01",
        "income": 15000.00,
        "expense": 8500.00,
        "balance": 6500.00,
        "transaction_count": 156,
        "income_growth_rate": null,
        "expense_growth_rate": null
      },
      {
        "month": "2024-02",
        "income": 16000.00,
        "expense": 9200.00,
        "balance": 6800.00,
        "transaction_count": 142,
        "income_growth_rate": 6.67,
        "expense_growth_rate": 8.24
      },
      {
        "month": "2024-03",
        "income": 15500.00,
        "expense": 8800.00,
        "balance": 6700.00,
        "transaction_count": 168,
        "income_growth_rate": -3.13,
        "expense_growth_rate": -4.35
      }
    ],
    "summary": {
      "total_income": 92500.00,
      "total_expense": 51200.00,
      "total_balance": 41300.00,
      "avg_monthly_income": 15416.67,
      "avg_monthly_expense": 8533.33,
      "avg_monthly_balance": 6883.33
    }
  },
  "timestamp": 1704067200000
}
```

### 3.5 字段说明

- `months`: 月度数据数组
  - `income_growth_rate`: 收入环比增长率（%），首月为null
  - `expense_growth_rate`: 支出环比增长率（%），首月为null
- `summary`: 汇总统计
  - `avg_monthly_*`: 月均值

## 4. 年度统计总览接口

### 4.1 接口信息

- **路径**: `/api/v1/statistics/yearly-overview`
- **方法**: `GET`
- **描述**: 查询指定年度的统计总览数据

### 4.2 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| year | integer | 是 | 年份 | 2024 |
| account_id | integer | 否 | 账户ID | 1 |

### 4.3 请求示例

```
GET /api/v1/statistics/yearly-overview?year=2024
```

### 4.4 响应数据

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "year": 2024,
    "summary": {
      "total_income": 180000.00,
      "total_expense": 102000.00,
      "net_balance": 78000.00,
      "total_transaction_count": 1856,
      "avg_monthly_income": 15000.00,
      "avg_monthly_expense": 8500.00,
      "savings_rate": 43.33
    },
    "monthly_trend": [
      {
        "month": "2024-01",
        "income": 15000.00,
        "expense": 8500.00,
        "balance": 6500.00
      },
      {
        "month": "2024-02",
        "income": 16000.00,
        "expense": 9200.00,
        "balance": 6800.00
      }
    ],
    "top_expense_categories": [
      {
        "category_id": 1,
        "category_name": "餐饮",
        "amount": 38400.00,
        "percentage": 37.65,
        "transaction_count": 540
      },
      {
        "category_id": 2,
        "category_name": "交通",
        "amount": 18000.00,
        "percentage": 17.65,
        "transaction_count": 360
      }
    ],
    "top_income_categories": [
      {
        "category_id": 10,
        "category_name": "工资",
        "amount": 150000.00,
        "percentage": 83.33,
        "transaction_count": 12
      },
      {
        "category_id": 11,
        "category_name": "奖金",
        "amount": 20000.00,
        "percentage": 11.11,
        "transaction_count": 4
      }
    ],
    "peak_expense_month": {
      "month": "2024-12",
      "amount": 12500.00
    },
    "peak_income_month": {
      "month": "2024-12",
      "amount": 25000.00
    }
  },
  "timestamp": 1704067200000
}
```

### 4.5 字段说明

- `summary`: 年度汇总
  - `savings_rate`: 储蓄率（%）= (总收入-总支出)/总收入 * 100
- `monthly_trend`: 月度趋势（12个月）
- `top_expense_categories`: 支出前5分类
- `top_income_categories`: 收入前5分类
- `peak_expense_month`: 支出最高月份
- `peak_income_month`: 收入最高月份

## 5. 关键指标查询接口

### 5.1 接口信息

- **路径**: `/api/v1/statistics/key-metrics`
- **方法**: `GET`
- **描述**: 查询关键财务指标，默认返回当前月数据

### 5.2 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| month | string | 否 | 月份 (YYYY-MM)，默认当前月 | 2024-01 |
| account_id | integer | 否 | 账户ID | 1 |

### 5.3 请求示例

```
GET /api/v1/statistics/key-metrics?month=2024-01
```

### 5.4 响应数据

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "month": "2024-01",
    "current_month": {
      "total_income": 15000.00,
      "total_expense": 8500.00,
      "balance": 6500.00,
      "transaction_count": 156,
      "avg_daily_expense": 274.19,
      "budget_usage_rate": 85.00,
      "savings_rate": 43.33
    },
    "comparison_with_last_month": {
      "income_change": 1000.00,
      "income_change_rate": 7.14,
      "expense_change": 500.00,
      "expense_change_rate": 6.25,
      "balance_change": 500.00,
      "balance_change_rate": 8.33
    },
    "comparison_with_same_month_last_year": {
      "income_change": 2000.00,
      "income_change_rate": 15.38,
      "expense_change": 800.00,
      "expense_change_rate": 10.39,
      "balance_change": 1200.00,
      "balance_change_rate": 22.64
    },
    "budget_status": {
      "total_budget": 10000.00,
      "used_amount": 8500.00,
      "remaining_amount": 1500.00,
      "usage_rate": 85.00,
      "days_remaining": 15,
      "estimated_overspend": 0.00
    },
    "top_expense_category": {
      "category_id": 1,
      "category_name": "餐饮",
      "amount": 3200.00,
      "percentage": 37.65
    },
    "largest_single_expense": {
      "transaction_id": 12345,
      "amount": 2500.00,
      "category_name": "购物",
      "description": "购买笔记本电脑",
      "date": "2024-01-15"
    }
  },
  "timestamp": 1704067200000
}
```

### 5.5 字段说明

- `current_month`: 当月指标
  - `avg_daily_expense`: 日均支出
  - `budget_usage_rate`: 预算使用率（%）
  - `savings_rate`: 储蓄率（%）
- `comparison_with_last_month`: 环比上月
  - `*_change`: 变化金额（正数表示增加）
  - `*_change_rate`: 变化率（%）
- `comparison_with_same_month_last_year`: 同比去年同月
- `budget_status`: 预算状态
  - `days_remaining`: 本月剩余天数
  - `estimated_overspend`: 预计超支金额（基于当前消费速度）
- `top_expense_category`: 最大支出分类
- `largest_single_expense`: 最大单笔支出

## 6. 通用错误码

| 错误码 | 说明 | HTTP状态码 |
|--------|------|-----------|
| 0 | 成功 | 200 |
| 1001 | 参数错误 | 400 |
| 1002 | 日期格式错误 | 400 |
| 1003 | 日期范围无效（开始日期晚于结束日期） | 400 |
| 1004 | 日期范围过大（超过限制） | 400 |
| 1005 | 维度参数无效 | 400 |
| 1006 | 类型参数无效 | 400 |
| 2001 | 未授权 | 401 |
| 2002 | Token过期 | 401 |
| 2003 | 无权限访问 | 403 |
| 3001 | 账户不存在 | 404 |
| 3002 | 分类不存在 | 404 |
| 3003 | 数据不存在 | 404 |
| 5001 | 服务器内部错误 | 500 |
| 5002 | 数据库错误 | 500 |

### 6.1 错误响应示例

```json
{
  "code": 1002,
  "message": "日期格式错误，请使用 YYYY-MM-DD 格式",
  "data": null,
  "timestamp": 1704067200000
}
```

## 7. 接口限制说明

### 7.1 时间范围限制

- 收支趋势查询：
  - day 维度：最大查询 366 天
  - week 维度：最大查询 104 周（约2年）
  - month 维度：最大查询 36 个月（3年）
- 月度对比：最大查询 24 个月
- 年度总览：仅支持单年查询

### 7.2 性能优化建议

- 大范围查询建议使用更粗粒度的维度（如用 month 代替 day）
- 分类占比统计建议使用 `top_n` 参数限制返回数量
- 频繁查询的数据建议客户端缓存

### 7.3 数据更新说明

- 统计数据基于交易记录实时计算
- 复杂统计可能存在秒级延迟
- 历史数据修改会影响统计结果

## 8. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2024-01-01 | 初始版本 |

## 9. 联系方式

如有问题或建议，请联系：
- API 文档：https://api.example.com/docs
- 技术支持：support@example.com