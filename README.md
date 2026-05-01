# Bill Management System - Query API

## Overview

This module implements a comprehensive bill query API with advanced filtering, pagination, and statistics capabilities.

## Features

### Query Capabilities

- **Time Range Filtering**: Query bills within a specific date range
- **Category Filtering**: Filter by bill category
- **Type Filtering**: Filter by income or expense
- **Amount Range**: Filter by minimum and maximum amount
- **Keyword Search**: Search bills by description keyword
- **Pagination**: Efficient pagination with configurable page size
- **Sorting**: Sort by date, amount, or creation time (ascending/descending)

### Performance Optimization

**Database Indexes**:
- `idx_bills_date`: Optimizes time range queries
- `idx_bills_category`: Speeds up category filtering
- `idx_bills_type`: Optimizes type filtering
- `idx_bills_amount`: Improves amount range queries
- `idx_bills_type_date`: Composite index for common type+date queries
- `idx_bills_category_date`: Composite index for category+date queries
- `idx_bills_created_at`: Optimizes sorting by creation time

## API Endpoints

### 1. Query Bills

**Endpoint**: `GET /api/bills/query`

**Query Parameters**:
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `category` (optional): Bill category
- `bill_type` (optional): "income" or "expense"
- `min_amount` (optional): Minimum amount
- `max_amount` (optional): Maximum amount
- `keyword` (optional): Search keyword in description
- `page` (default: 1): Page number
- `page_size` (default: 20, max: 100): Items per page
- `sort_by` (default: "date"): Sort field (date/amount/created_at)
- `sort_order` (default: "desc"): Sort order (asc/desc)

**Response**:
```json
{
  "items": [
    {
      "id": 1,
      "bill_type": "expense",
      "category": "food",
      "amount": 50.00,
      "date": "2024-01-15",
      "description": "Lunch",
      "created_at": "2024-01-15T12:00:00",
      "updated_at": "2024-01-15T12:00:00"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5,
  "has_next": true,
  "has_prev": false
}
```

### 2. Get Statistics

**Endpoint**: `GET /api/bills/statistics`

**Query Parameters**:
- `start_date` (optional): Start date filter
- `end_date` (optional): End date filter
- `category` (optional): Category filter

**Response**:
```json
{
  "total_income": 5000.00,
  "total_expense": 3000.00,
  "net_amount": 2000.00,
  "count": 150
}
```

## Usage Examples

### Query bills in a date range
```bash
curl "http://localhost:8080/api/bills/query?start_date=2024-01-01&end_date=2024-01-31"
```

### Query expenses in a category
```bash
curl "http://localhost:8080/api/bills/query?bill_type=expense&category=food"
```

### Query with amount range and keyword
```bash
curl "http://localhost:8080/api/bills/query?min_amount=100&max_amount=500&keyword=restaurant"
```

### Get statistics for current month
```bash
curl "http://localhost:8080/api/bills/statistics?start_date=2024-01-01&end_date=2024-01-31"
```

## Database Migration

Indexes are automatically created on application startup. To manually apply indexes:

```bash
sqlite3 bills.db < backend/database/migrations/add_bill_indexes.sql
```

## Performance Considerations

1. **Index Usage**: All filter fields are indexed for optimal query performance
2. **Pagination**: Always use pagination for large result sets
3. **Composite Indexes**: Common query patterns (type+date, category+date) use composite indexes
4. **Connection Timeout**: Database connections have a 5-second timeout to prevent locks

## Development

### Run Backend
```bash
python backend/main.py
```

### Test Query API
```bash
# Install httpx for testing
pip install httpx pytest

# Run tests
pytest tests/test_bill_query.py
```

## Security Notes

- All user inputs are validated using Pydantic models
- SQL injection prevention through parameterized queries
- Amount fields validated to be non-negative
- Date format strictly validated (YYYY-MM-DD)
- Page size limited to maximum 100 items
