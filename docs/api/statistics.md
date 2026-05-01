# 统计数据聚合 API 文档

## 概述

本文档定义了记账应用统计数据聚合相关的 API 接口规范，包括收支趋势、分类占比、月度对比、年度总览和关键指标等统计功能。

**基础路径**: `/api/v1/statistics`

**认证方式**: Bearer Token (JWT)

---

## 1. 收支趋势查询接口

### 1.1 接口信息

- **路径**: `/api/v1/statistics/trends`
- **方法**: `GET`
- **描述**: 查询指定时间范围内的收支趋势数据，支持按日、周、月维度聚合

### 1.2 请求参数

#### Query Parameters

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| dimension | string | 是 | 统计维度：day/week/month | day |
| start_date | string | 是 | 开始日期 (YYYY-MM-DD) | 2024-01-01 |
| end_date | string | 是 | 结束日期 (YYYY-MM-DD) | 2024-01-31 |
| type | string | 否 | 交易类型：income/expense/all，默认 all | all |

### 1.3 请求示例

```http
GET /api/v1/statistics/trends?dimension=day&start_date=2024-01-01&end_date=2024-01-31&type=all
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 1.4 响应格式

#### 成功响应 (200 OK)

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "dimension": "day",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "trends": [
      {
        "date": "2024-01-01",
        "income": 5000.00,
        "expense": 1200.50,
        "balance": 3799.50
      },
      {
        "date": "2024-01-02",
        "income": 0.00,
        "expense": 350.00,
        "balance": -350.00
      }
    ],
    "summary": {
      "total_income": 15000.00,
      "total_expense": 8500.00,
      "net_balance": 6500.00
    }
  }
}
```

---

## 2. 分类占比统计接口

### 2.1 接口信息

- **路径**: `/api/v1/statistics/category-distribution`
- **方法**: `GET`
- **描述**: 统计指定时间范围内各分类的金额占比

### 2.2 请求参数

#### Query Parameters

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| type | string | 是 | 交易类型：income/expense | expense |
| start_date | string | 是 | 开始日期 (YYYY-MM-DD) | 2024-01-01 |
| end_date | string | 是 | 结束日期 (YYYY-MM-DD) | 2024-01-31 |
| top_n | integer | 否 | 返回前 N 个分类，默认 10 | 5 |

### 2.3 请求示例

```http
GET /api/v1/statistics/category-distribution?type=expense&start_date=2024-01-01&end_date=2024-01-31&top_n=5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2.4 响应格式

#### 成功响应 (200 OK)

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
        "amount": 3200.00,
        "percentage": 37.65,
        "transaction_count": 45
      },
      {
        "category_id": 2,
        "category_name": "交通",
        "amount": 1500.00,
        "percentage": 17.65,
        "transaction_count": 30
      },
      {
        "category_id": 3,
        "category_name": "购物",
        "amount": 2000.00,
        "percentage": 23.53,
        "transaction_count": 12
      },
      {
        "category_id": 4,
        "category_name": "娱乐",
        "amount": 800.00,
        "percentage": 9.41,
        "transaction_count": 8
      },
      {
        "category_id": 5,
        "category_name": "其他",
        "amount": 1000.00,
        "percentage": 11.76,
        "transaction_count": 15
      }
    ]
  }
}
```

---

## 3. 月度收支对比接口

### 3.1 接口信息

- **路径**: `/api/v1/statistics/monthly-comparison`
- **方法**: `GET`
- **描述**: 对比多个月份的收支情况

### 3.2 请求参数

#### Query Parameters

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| months | string | 是 | 月份列表，逗号分隔 (YYYY-MM) | 2024-01,2024-02,2024-03 |
| year | integer | 否 | 年份，返回该年所有月份，与 months 二选一 | 2024 |

### 3.3 请求示例

```http
GET /api/v1/statistics/monthly-comparison?months=2024-01,2024-02,2024-03
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

或

```http
GET /api/v1/statistics/monthly-comparison?year=2024
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3.4 响应格式

#### 成功响应 (200 OK)

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "comparison": [
      {
        "month": "2024-01",
        "income": 15000.00,
        "expense": 8500.00,
        "balance": 6500.00,
        "income_change_rate": null,
        "expense_change_rate": null,
        "transaction_count": 120
      },
      {
        "month": "2024-02",
        "income": 16000.00,
        "expense": 9200.00,
        "balance": 6800.00,
        "income_change_rate": 6.67,
        "expense_change_rate": 8.24,
        "transaction_count": 135
      },
      {
        "month": "2024-03",
        "income": 15500.00,
        "expense": 8800.00,
        "balance": 6700.00,
        "income_change_rate": -3.13,
        "expense_change_rate": -4.35,
        "transaction_count": 128
      }
    ],
    "average": {
      "avg_income": 15500.00,
      "avg_expense": 8833.33,
      "avg_balance": 6666.67
    }
  }
}
```

---

## 4. 年度统计总览接口

### 4.1 接口信息

- **路径**: `/api/v1/statistics/annual-overview`
- **方法**: `GET`
- **描述**: 获取指定年份的统计总览数据

### 4.2 请求参数

#### Query Parameters

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| year | integer | 是 | 年份 | 2024 |

### 4.3 请求示例

```http
GET /api/v1/statistics/annual-overview?year=2024
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4.4 响应格式

#### 成功响应 (200 OK)

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "year": 2024,
    "summary": {
      "total_income": 180000.00,
      "total_expense": 105000.00,
      "net_balance": 75000.00,
      "transaction_count": 1450,
      "avg_monthly_income": 15000.00,
      "avg_monthly_expense": 8750.00
    },
    "monthly_data": [
      {
        "month": 1,
        "income": 15000.00,
        "expense": 8500.00,
        "balance": 6500.00
      },
      {
        "month": 2,
        "income": 16000.00,
        "expense": 9200.00,
        "balance": 6800.00
      }
    ],
    "top_income_categories": [
      {
        "category_id": 10,
        "category_name": "工资",
        "amount": 150000.00,
        "percentage": 83.33
      },
      {
        "category_id": 11,
        "category_name": "奖金",
        "amount": 20000.00,
        "percentage": 11.11
      }
    ],
    "top_expense_categories": [
      {
        "category_id": 1,
        "category_name": "餐饮",
        "amount": 38000.00,
        "percentage": 36.19
      },
      {
        "category_id": 2,
        "category_name": "交通",
        "amount": 18000.00,
        "percentage": 17.14
      }
    ],
    "peak_expense_month": {
      "month": 12,
      "amount": 12000.00
    },
    "peak_income_month": {
      "month": 12,
      "amount": 25000.00
    }
  }
}
```

---

## 5. 关键指标查询接口

### 5.1 接口信息

- **路径**: `/api/v1/statistics/key-metrics`
- **方法**: `GET`
- **描述**: 查询关键财务指标，包括本月总收入、总支出、结余等

### 5.2 请求参数

#### Query Parameters

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| period | string | 否 | 统计周期：current_month/last_month/current_year，默认 current_month | current_month |

### 5.3 请求示例

```http
GET /api/v1/statistics/key-metrics?period=current_month
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5.4 响应格式

#### 成功响应 (200 OK)

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
      "total_expense": 8500.00,
      "net_balance": 6500.00,
      "transaction_count": 120,
      "avg_daily_expense": 274.19,
      "avg_transaction_amount": 195.83,
      "savings_rate": 43.33
    },
    "comparison_with_last_period": {
      "income_change": 1000.00,
      "income_change_rate": 7.14,
      "expense_change": 500.00,
      "expense_change_rate": 6.25,
      "balance_change": 500.00,
      "balance_change_rate": 8.33
    },
    "budget_status": {
      "total_budget": 10000.00,
      "used_budget": 8500.00,
      "remaining_budget": 1500.00,
      "usage_rate": 85.00,
      "is_over_budget": false
    },
    "top_expense_category": {
      "category_id": 1,
      "category_name": "餐饮",
      "amount": 3200.00,
      "percentage": 37.65
    },
    "largest_single_expense": {
      "transaction_id": 12345,
      "amount": 2000.00,
      "category_name": "购物",
      "description": "购买电子产品",
      "date": "2024-01-15"
    }
  }
}
```

---

## 6. 通用错误码

所有接口遵循统一的错误码规范：

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| 0 | 200 | 成功 |
| 1001 | 400 | 请求参数错误 |
| 1002 | 400 | 参数验证失败 |
| 1003 | 400 | 日期格式错误 |
| 1004 | 400 | 日期范围无效（开始日期晚于结束日期） |
| 1005 | 400 | 统计维度不支持 |
| 1006 | 400 | 交易类型不支持 |
| 2001 | 401 | 未授权，Token 缺失或无效 |
| 2002 | 401 | Token 已过期 |
| 3001 | 403 | 无权限访问 |
| 4001 | 404 | 资源不存在 |
| 5001 | 500 | 服务器内部错误 |
| 5002 | 500 | 数据库查询错误 |
| 5003 | 503 | 服务暂时不可用 |

### 错误响应格式

```json
{
  "code": 1003,
  "message": "日期格式错误，请使用 YYYY-MM-DD 格式",
  "data": null,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 7. 数据类型说明

### 7.1 统计维度 (dimension)

- `day`: 按日统计
- `week`: 按周统计（周一为起始日）
- `month`: 按月统计

### 7.2 交易类型 (type)

- `income`: 收入
- `expense`: 支出
- `all`: 全部（仅适用于趋势查询）

### 7.3 统计周期 (period)

- `current_month`: 当前月份
- `last_month`: 上个月
- `current_year`: 当前年度

---

## 8. 注意事项

1. **日期范围限制**: 单次查询的日期范围不超过 366 天
2. **数据精度**: 所有金额字段保留两位小数
3. **百分比计算**: 百分比字段保留两位小数，单位为 %
4. **时区处理**: 所有日期时间使用 UTC 时区，客户端需自行转换
5. **数据缓存**: 统计数据可能存在最多 5 分钟的缓存延迟
6. **并发限制**: 单用户每分钟最多调用统计接口 60 次
7. **数据权限**: 用户只能查询自己的统计数据

---

## 9. 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2024-01-15 | 初始版本，定义基础统计接口 |

---

## 10. 联系方式

如有问题或建议，请联系：

- **技术支持**: support@example.com
- **API 文档**: https://api.example.com/docs