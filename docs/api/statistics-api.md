# Statistics API Documentation

## Overview

This document defines the API specifications for statistics data aggregation endpoints. These APIs provide various statistical views of financial transactions including trends, category distributions, and key metrics.

## Base URL

```
/api/v1/statistics
```

## Authentication

All endpoints require authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Common Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 401 | Unauthorized | Invalid or missing authentication token |
| 403 | Forbidden | User does not have permission to access the resource |
| 400 | Bad Request | Invalid request parameters |
| 500 | Internal Server Error | Server encountered an unexpected error |

## Endpoints

### 1. Get Transaction Trends

Retrieve transaction trends aggregated by specified time dimension.

**Endpoint:** `GET /api/v1/statistics/trends`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| dimension | string | Yes | Time dimension: `day`, `week`, `month` |
| start_date | string | Yes | Start date in ISO 8601 format (YYYY-MM-DD) |
| end_date | string | Yes | End date in ISO 8601 format (YYYY-MM-DD) |
| type | string | No | Transaction type: `income`, `expense`, `all` (default: `all`) |
| category_id | integer | No | Filter by specific category ID |

**Request Example:**

```http
GET /api/v1/statistics/trends?dimension=month&start_date=2024-01-01&end_date=2024-12-31&type=all
```

**Response Schema:**

```json
{
  "code": 200,
  "message": "Success",
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
        "expense": 8500.00,
        "balance": 6500.00,
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
      "total_income": 31000.00,
      "total_expense": 17700.00,
      "total_balance": 13300.00,
      "total_transactions": 97,
      "average_income": 15500.00,
      "average_expense": 8850.00
    }
  }
}
```

**Error Responses:**

- `400 Bad Request`: Invalid dimension or date format
  ```json
  {
    "code": 400,
    "message": "Invalid dimension. Must be one of: day, week, month",
    "data": null
  }
  ```

---

### 2. Get Category Distribution

Retrieve transaction distribution by categories with percentage calculations.

**Endpoint:** `GET /api/v1/statistics/category-distribution`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| type | string | Yes | Transaction type: `income` or `expense` |
| start_date | string | Yes | Start date in ISO 8601 format (YYYY-MM-DD) |
| end_date | string | Yes | End date in ISO 8601 format (YYYY-MM-DD) |
| top_n | integer | No | Return top N categories (default: all) |

**Request Example:**

```http
GET /api/v1/statistics/category-distribution?type=expense&start_date=2024-01-01&end_date=2024-12-31&top_n=5
```

**Response Schema:**

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "type": "expense",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "total_amount": 102000.00,
    "categories": [
      {
        "category_id": 1,
        "category_name": "Food & Dining",
        "amount": 35000.00,
        "percentage": 34.31,
        "transaction_count": 156,
        "average_amount": 224.36
      },
      {
        "category_id": 2,
        "category_name": "Transportation",
        "amount": 18000.00,
        "percentage": 17.65,
        "transaction_count": 89,
        "average_amount": 202.25
      },
      {
        "category_id": 3,
        "category_name": "Shopping",
        "amount": 25000.00,
        "percentage": 24.51,
        "transaction_count": 67,
        "average_amount": 373.13
      },
      {
        "category_id": 4,
        "category_name": "Entertainment",
        "amount": 12000.00,
        "percentage": 11.76,
        "transaction_count": 45,
        "average_amount": 266.67
      },
      {
        "category_id": 5,
        "category_name": "Healthcare",
        "amount": 8000.00,
        "percentage": 7.84,
        "transaction_count": 23,
        "average_amount": 347.83
      }
    ],
    "others": {
      "amount": 4000.00,
      "percentage": 3.92,
      "transaction_count": 28
    }
  }
}
```

**Error Responses:**

- `400 Bad Request`: Invalid transaction type
  ```json
  {
    "code": 400,
    "message": "Invalid type. Must be either 'income' or 'expense'",
    "data": null
  }
  ```

---

### 3. Get Monthly Comparison

Compare income and expense data across multiple months.

**Endpoint:** `GET /api/v1/statistics/monthly-comparison`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| year | integer | Yes | Year for comparison (YYYY) |
| months | string | No | Comma-separated month numbers (1-12). Default: all months |

**Request Example:**

```http
GET /api/v1/statistics/monthly-comparison?year=2024&months=1,2,3,4,5,6
```

**Response Schema:**

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "year": 2024,
    "months": [
      {
        "month": 1,
        "month_name": "January",
        "income": 15000.00,
        "expense": 8500.00,
        "balance": 6500.00,
        "savings_rate": 43.33,
        "transaction_count": 45,
        "income_growth": null,
        "expense_growth": null
      },
      {
        "month": 2,
        "month_name": "February",
        "income": 16000.00,
        "expense": 9200.00,
        "balance": 6800.00,
        "savings_rate": 42.50,
        "transaction_count": 52,
        "income_growth": 6.67,
        "expense_growth": 8.24
      },
      {
        "month": 3,
        "month_name": "March",
        "income": 15500.00,
        "expense": 8800.00,
        "balance": 6700.00,
        "savings_rate": 43.23,
        "transaction_count": 48,
        "income_growth": -3.13,
        "expense_growth": -4.35
      }
    ],
    "summary": {
      "total_income": 46500.00,
      "total_expense": 26500.00,
      "total_balance": 20000.00,
      "average_income": 15500.00,
      "average_expense": 8833.33,
      "average_savings_rate": 43.01,
      "highest_income_month": 2,
      "highest_expense_month": 2,
      "lowest_expense_month": 1
    }
  }
}
```

**Error Responses:**

- `400 Bad Request`: Invalid year or month values
  ```json
  {
    "code": 400,
    "message": "Invalid month value. Must be between 1 and 12",
    "data": null
  }
  ```

---

### 4. Get Annual Overview

Retrieve comprehensive annual statistics overview.

**Endpoint:** `GET /api/v1/statistics/annual-overview`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| year | integer | Yes | Year for overview (YYYY) |

**Request Example:**

```http
GET /api/v1/statistics/annual-overview?year=2024
```

**Response Schema:**

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "year": 2024,
    "financial_summary": {
      "total_income": 180000.00,
      "total_expense": 102000.00,
      "total_balance": 78000.00,
      "savings_rate": 43.33,
      "transaction_count": 567
    },
    "monthly_average": {
      "income": 15000.00,
      "expense": 8500.00,
      "balance": 6500.00
    },
    "peak_months": {
      "highest_income": {
        "month": 12,
        "month_name": "December",
        "amount": 25000.00
      },
      "highest_expense": {
        "month": 11,
        "month_name": "November",
        "amount": 15000.00
      },
      "highest_balance": {
        "month": 12,
        "month_name": "December",
        "amount": 12000.00
      }
    },
    "top_expense_categories": [
      {
        "category_id": 1,
        "category_name": "Food & Dining",
        "amount": 35000.00,
        "percentage": 34.31
      },
      {
        "category_id": 3,
        "category_name": "Shopping",
        "amount": 25000.00,
        "percentage": 24.51
      },
      {
        "category_id": 2,
        "category_name": "Transportation",
        "amount": 18000.00,
        "percentage": 17.65
      }
    ],
    "top_income_categories": [
      {
        "category_id": 10,
        "category_name": "Salary",
        "amount": 150000.00,
        "percentage": 83.33
      },
      {
        "category_id": 11,
        "category_name": "Investment",
        "amount": 20000.00,
        "percentage": 11.11
      },
      {
        "category_id": 12,
        "category_name": "Bonus",
        "amount": 10000.00,
        "percentage": 5.56
      }
    ],
    "quarterly_breakdown": [
      {
        "quarter": 1,
        "quarter_name": "Q1",
        "income": 45000.00,
        "expense": 25500.00,
        "balance": 19500.00
      },
      {
        "quarter": 2,
        "quarter_name": "Q2",
        "income": 46000.00,
        "expense": 26000.00,
        "balance": 20000.00
      },
      {
        "quarter": 3,
        "quarter_name": "Q3",
        "income": 44000.00,
        "expense": 25500.00,
        "balance": 18500.00
      },
      {
        "quarter": 4,
        "quarter_name": "Q4",
        "income": 45000.00,
        "expense": 25000.00,
        "balance": 20000.00
      }
    ],
    "year_over_year": {
      "income_growth": 12.50,
      "expense_growth": 8.00,
      "balance_growth": 18.18
    }
  }
}
```

**Error Responses:**

- `400 Bad Request`: Invalid year
  ```json
  {
    "code": 400,
    "message": "Invalid year format",
    "data": null
  }
  ```

---

### 5. Get Key Metrics

Retrieve key financial metrics for a specific period.

**Endpoint:** `GET /api/v1/statistics/key-metrics`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| period | string | Yes | Period type: `current_month`, `last_month`, `current_year`, `custom` |
| start_date | string | Conditional | Required if period is `custom` (YYYY-MM-DD) |
| end_date | string | Conditional | Required if period is `custom` (YYYY-MM-DD) |

**Request Example:**

```http
GET /api/v1/statistics/key-metrics?period=current_month
```

**Response Schema:**

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "period": "current_month",
    "period_start": "2024-12-01",
    "period_end": "2024-12-31",
    "metrics": {
      "total_income": 16000.00,
      "total_expense": 9200.00,
      "balance": 6800.00,
      "savings_rate": 42.50,
      "transaction_count": 52,
      "average_transaction_amount": 484.62,
      "daily_average_expense": 296.77,
      "daily_average_income": 516.13
    },
    "comparison": {
      "previous_period": {
        "period_start": "2024-11-01",
        "period_end": "2024-11-30",
        "total_income": 15000.00,
        "total_expense": 8500.00,
        "balance": 6500.00
      },
      "income_change": {
        "amount": 1000.00,
        "percentage": 6.67
      },
      "expense_change": {
        "amount": 700.00,
        "percentage": 8.24
      },
      "balance_change": {
        "amount": 300.00,
        "percentage": 4.62
      }
    },
    "budget_status": {
      "has_budget": true,
      "budget_amount": 10000.00,
      "spent_amount": 9200.00,
      "remaining_amount": 800.00,
      "utilization_rate": 92.00,
      "status": "warning"
    },
    "top_expense": {
      "category_name": "Food & Dining",
      "amount": 3200.00,
      "percentage": 34.78
    },
    "top_income": {
      "category_name": "Salary",
      "amount": 15000.00,
      "percentage": 93.75
    }
  }
}
```

**Error Responses:**

- `400 Bad Request`: Missing required parameters for custom period
  ```json
  {
    "code": 400,
    "message": "start_date and end_date are required when period is 'custom'",
    "data": null
  }
  ```

- `400 Bad Request`: Invalid period type
  ```json
  {
    "code": 400,
    "message": "Invalid period. Must be one of: current_month, last_month, current_year, custom",
    "data": null
  }
  ```

---

## Data Types

### Period Dimension

- `day`: Daily aggregation
- `week`: Weekly aggregation (Monday to Sunday)
- `month`: Monthly aggregation

### Transaction Type

- `income`: Income transactions only
- `expense`: Expense transactions only
- `all`: Both income and expense transactions

### Period Type

- `current_month`: Current calendar month
- `last_month`: Previous calendar month
- `current_year`: Current calendar year
- `custom`: Custom date range (requires start_date and end_date)

### Budget Status

- `safe`: Utilization rate < 70%
- `warning`: Utilization rate between 70% and 90%
- `danger`: Utilization rate > 90%
- `exceeded`: Spent amount exceeds budget

---

## Rate Limiting

All statistics endpoints are subject to rate limiting:

- **Rate Limit:** 100 requests per minute per user
- **Headers:**
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets (Unix timestamp)

**Rate Limit Exceeded Response:**

```json
{
  "code": 429,
  "message": "Rate limit exceeded. Please try again later.",
  "data": {
    "retry_after": 60
  }
}
```

---

## Notes

1. All monetary amounts are returned as decimal numbers with 2 decimal places
2. Percentages are returned as decimal numbers (e.g., 43.33 represents 43.33%)
3. Dates are in ISO 8601 format (YYYY-MM-DD)
4. All timestamps are in UTC
5. Growth rates are calculated as: ((current - previous) / previous) × 100
6. Savings rate is calculated as: (balance / income) × 100
7. Empty result sets will return empty arrays with appropriate summary values set to 0

---

## Changelog

### Version 1.0.0 (2024-01-01)
- Initial API specification release
- Added all five statistics endpoints
- Defined common error codes and response formats