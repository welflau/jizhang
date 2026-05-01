# 统计数据聚合 API 文档

## 概述

本文档定义了统计数据聚合相关的 API 接口规范，包括收支趋势、分类占比、月度对比、年度总览和关键指标查询等功能。

**基础路径**: `/api/v1/statistics`

**认证方式**: Bearer Token (JWT)

**通用请求头**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

---

## 1. 收支趋势查询接口

### 接口信息
- **路径**: `/api/v1/statistics/trends`
- **方法**: `GET`
- **描述**: 查询指定时间范围内的收支趋势数据，支持按日、周、月维度聚合

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| dimension | string | 是 | 聚合维度：`day`（日）、`week`（周）、`month`（月） |
| start_date | string | 是 | 开始日期，格式：YYYY-MM-DD |
| end_date | string | 是 | 结束日期，格式：YYYY-MM-DD |
| type | string | 否 | 交易类型：`income`（收入）、`expense`（支出）、`all`（全部，默认） |
| category_ids | array | 否 | 分类 ID 列表，用于筛选特定分类 |

### 请求示例

```http
GET /api/v1/statistics/trends?dimension=month&start_date=2024-01-01&end_date=2024-12-31&type=all
```

### 响应格式

**成功响应 (200)**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "dimension": "month",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "trends": [
      {
        "period": "2024-01",
        "period_start": "2024-01-01",
        "period_end": "2024-01-31",
        "income": 15000.00,
        "expense": 8500.50,
        "balance": 6499.50,
        "transaction_count": 45
      },
      {
        "period": "2024-02",
        "period_start": "2024-02-01",
        "period_end": "2024-02-29",
        "income": 16000.00,
        "expense": 9200.00,
        "balance": 6800.00,
        "transaction_count": 52
      }
    ],
    "summary": {
      "total_income": 186000.00,
      "total_expense": 105000.00,
      "total_balance": 81000.00,
      "avg_income": 15500.00,
      "avg_expense": 8750.00,
      "total_transactions": 568
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 参数验证失败 |
| 1002 | 日期格式错误 |
| 1003 | 日期范围无效（结束日期早于开始日期） |
| 1004 | 日期范围超出限制（最多查询 2 年数据） |
| 4001 | 未授权访问 |
| 5001 | 服务器内部错误 |

---

## 2. 分类占比统计接口

### 接口信息
- **路径**: `/api/v1/statistics/category-distribution`
- **方法**: `GET`
- **描述**: 统计指定时间范围内各分类的金额占比，支持按收入或支出分别统计

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| type | string | 是 | 交易类型：`income`（收入）、`expense`（支出） |
| start_date | string | 是 | 开始日期，格式：YYYY-MM-DD |
| end_date | string | 是 | 结束日期，格式：YYYY-MM-DD |
| top_n | integer | 否 | 返回前 N 个分类，默认返回全部，其余归入"其他" |
| min_percentage | float | 否 | 最小占比阈值（0-100），低于此值的归入"其他" |

### 请求示例

```http
GET /api/v1/statistics/category-distribution?type=expense&start_date=2024-01-01&end_date=2024-12-31&top_n=10
```

### 响应格式

**成功响应 (200)**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "type": "expense",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "total_amount": 105000.00,
    "categories": [
      {
        "category_id": 101,
        "category_name": "餐饮美食",
        "category_icon": "food",
        "amount": 28500.00,
        "percentage": 27.14,
        "transaction_count": 156,
        "avg_amount": 182.69
      },
      {
        "category_id": 102,
        "category_name": "交通出行",
        "category_icon": "transport",
        "amount": 15600.00,
        "percentage": 14.86,
        "transaction_count": 89,
        "avg_amount": 175.28
      },
      {
        "category_id": 103,
        "category_name": "购物消费",
        "category_icon": "shopping",
        "amount": 21000.00,
        "percentage": 20.00,
        "transaction_count": 45,
        "avg_amount": 466.67
      }
    ],
    "others": {
      "amount": 5200.00,
      "percentage": 4.95,
      "transaction_count": 32,
      "category_count": 8
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 参数验证失败 |
| 1002 | 日期格式错误 |
| 1005 | 交易类型无效 |
| 4001 | 未授权访问 |
| 5001 | 服务器内部错误 |

---

## 3. 月度收支对比接口

### 接口信息
- **路径**: `/api/v1/statistics/monthly-comparison`
- **方法**: `GET`
- **描述**: 对比多个月份的收支情况，支持同比、环比分析

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| months | array | 是 | 月份列表，格式：YYYY-MM，最多支持 12 个月 |
| compare_type | string | 否 | 对比类型：`yoy`（同比）、`mom`（环比）、`none`（不对比，默认） |

### 请求示例

```http
GET /api/v1/statistics/monthly-comparison?months=2024-01,2024-02,2024-03&compare_type=mom
```

### 响应格式

**成功响应 (200)**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "compare_type": "mom",
    "months": [
      {
        "month": "2024-01",
        "income": 15000.00,
        "expense": 8500.50,
        "balance": 6499.50,
        "transaction_count": 45,
        "income_change": null,
        "expense_change": null,
        "balance_change": null,
        "income_change_rate": null,
        "expense_change_rate": null
      },
      {
        "month": "2024-02",
        "income": 16000.00,
        "expense": 9200.00,
        "balance": 6800.00,
        "transaction_count": 52,
        "income_change": 1000.00,
        "expense_change": 699.50,
        "balance_change": 300.50,
        "income_change_rate": 6.67,
        "expense_change_rate": 8.23
      },
      {
        "month": "2024-03",
        "income": 15500.00,
        "expense": 8800.00,
        "balance": 6700.00,
        "transaction_count": 48,
        "income_change": -500.00,
        "expense_change": -400.00,
        "balance_change": -100.00,
        "income_change_rate": -3.13,
        "expense_change_rate": -4.35
      }
    ],
    "summary": {
      "total_income": 46500.00,
      "total_expense": 26500.50,
      "total_balance": 19999.50,
      "avg_income": 15500.00,
      "avg_expense": 8833.50,
      "avg_balance": 6666.50
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 参数验证失败 |
| 1006 | 月份格式错误 |
| 1007 | 月份数量超出限制 |
| 4001 | 未授权访问 |
| 5001 | 服务器内部错误 |

---

## 4. 年度统计总览接口

### 接口信息
- **路径**: `/api/v1/statistics/yearly-overview`
- **方法**: `GET`
- **描述**: 获取指定年份的统计总览，包括月度数据、分类汇总、关键指标等

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| year | integer | 是 | 年份，格式：YYYY |

### 请求示例

```http
GET /api/v1/statistics/yearly-overview?year=2024
```

### 响应格式

**成功响应 (200)**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "year": 2024,
    "summary": {
      "total_income": 186000.00,
      "total_expense": 105000.00,
      "total_balance": 81000.00,
      "total_transactions": 568,
      "avg_monthly_income": 15500.00,
      "avg_monthly_expense": 8750.00,
      "savings_rate": 43.55
    },
    "monthly_data": [
      {
        "month": 1,
        "income": 15000.00,
        "expense": 8500.50,
        "balance": 6499.50,
        "transaction_count": 45
      },
      {
        "month": 2,
        "income": 16000.00,
        "expense": 9200.00,
        "balance": 6800.00,
        "transaction_count": 52
      }
    ],
    "top_expense_categories": [
      {
        "category_id": 101,
        "category_name": "餐饮美食",
        "amount": 28500.00,
        "percentage": 27.14,
        "transaction_count": 156
      },
      {
        "category_id": 102,
        "category_name": "交通出行",
        "amount": 15600.00,
        "percentage": 14.86,
        "transaction_count": 89
      }
    ],
    "top_income_categories": [
      {
        "category_id": 201,
        "category_name": "工资收入",
        "amount": 150000.00,
        "percentage": 80.65,
        "transaction_count": 12
      },
      {
        "category_id": 202,
        "category_name": "投资收益",
        "amount": 25000.00,
        "percentage": 13.44,
        "transaction_count": 8
      }
    ],
    "peak_expense_month": {
      "month": 12,
      "amount": 12500.00
    },
    "peak_income_month": {
      "month": 12,
      "amount": 20000.00
    },
    "comparison_with_last_year": {
      "income_change": 12000.00,
      "income_change_rate": 6.90,
      "expense_change": 8500.00,
      "expense_change_rate": 8.81,
      "balance_change": 3500.00,
      "balance_change_rate": 4.52
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 参数验证失败 |
| 1008 | 年份格式错误 |
| 1009 | 年份超出查询范围 |
| 4001 | 未授权访问 |
| 5001 | 服务器内部错误 |

---

## 5. 关键指标查询接口

### 接口信息
- **路径**: `/api/v1/statistics/key-metrics`
- **方法**: `GET`
- **描述**: 查询指定时间范围的关键财务指标，包括总收入、总支出、结余等

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| period | string | 否 | 时间周期：`current_month`（本月，默认）、`last_month`（上月）、`current_year`（本年）、`custom`（自定义） |
| start_date | string | 否 | 开始日期（period=custom 时必填），格式：YYYY-MM-DD |
| end_date | string | 否 | 结束日期（period=custom 时必填），格式：YYYY-MM-DD |

### 请求示例

```http
GET /api/v1/statistics/key-metrics?period=current_month
```

### 响应格式

**成功响应 (200)**:

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "period": "current_month",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "metrics": {
      "total_income": 15000.00,
      "total_expense": 8500.50,
      "balance": 6499.50,
      "savings_rate": 43.33,
      "transaction_count": 45,
      "avg_transaction_amount": 522.22,
      "income_transaction_count": 5,
      "expense_transaction_count": 40,
      "avg_income_amount": 3000.00,
      "avg_expense_amount": 212.51,
      "daily_avg_expense": 274.21,
      "max_single_expense": 2500.00,
      "max_single_income": 12000.00
    },
    "comparison": {
      "vs_last_period": {
        "income_change": 1000.00,
        "income_change_rate": 7.14,
        "expense_change": 500.50,
        "expense_change_rate": 6.25,
        "balance_change": 499.50,
        "balance_change_rate": 8.33
      },
      "vs_same_period_last_year": {
        "income_change": 2000.00,
        "income_change_rate": 15.38,
        "expense_change": 1200.00,
        "expense_change_rate": 16.44,
        "balance_change": 800.00,
        "balance_change_rate": 14.04
      }
    },
    "budget_status": {
      "has_budget": true,
      "budget_amount": 10000.00,
      "used_amount": 8500.50,
      "remaining_amount": 1499.50,
      "usage_rate": 85.01,
      "is_exceeded": false
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 参数验证失败 |
| 1002 | 日期格式错误 |
| 1010 | 时间周期参数无效 |
| 4001 | 未授权访问 |
| 5001 | 服务器内部错误 |

---

## 通用错误响应格式

所有接口的错误响应格式统一如下：

```json
{
  "code": 1001,
  "message": "参数验证失败",
  "errors": [
    {
      "field": "start_date",
      "message": "日期格式错误，应为 YYYY-MM-DD"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 通用错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | 参数验证失败 |
| 1002 | 日期格式错误 |
| 1003 | 日期范围无效 |
| 1004 | 日期范围超出限制 |
| 1005 | 交易类型无效 |
| 1006 | 月份格式错误 |
| 1007 | 月份数量超出限制 |
| 1008 | 年份格式错误 |
| 1009 | 年份超出查询范围 |
| 1010 | 时间周期参数无效 |
| 4001 | 未授权访问 |
| 4003 | 无权限访问 |
| 4004 | 资源不存在 |
| 5001 | 服务器内部错误 |
| 5002 | 数据库错误 |
| 5003 | 服务暂时不可用 |

---

## 数据类型说明

### 金额字段
- 类型: `decimal(10,2)`
- 单位: 元（人民币）
- 精度: 保留两位小数

### 日期字段
- 格式: `YYYY-MM-DD`
- 时区: UTC
- 示例: `2024-01-15`

### 时间戳字段
- 格式: ISO 8601
- 时区: UTC
- 示例: `2024-01-15T10:30:00Z`

### 百分比字段
- 类型: `float`
- 范围: 0-100
- 精度: 保留两位小数

---

## 性能优化建议

1. **缓存策略**: 统计数据建议缓存 5-15 分钟，减少数据库查询压力
2. **分页查询**: 对于大数据量查询，建议实现分页功能
3. **异步处理**: 年度总览等复杂统计可考虑异步生成
4. **索引优化**: 确保日期、分类、用户 ID 等字段建立索引
5. **数据预聚合**: 对于频繁查询的统计维度，可预先聚合存储

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2024-01-15 | 初始版本，定义基础统计 API |

---

## 联系方式

如有问题或建议，请联系：
- 邮箱: api-support@example.com
- 文档仓库: https://github.com/example/api-docs