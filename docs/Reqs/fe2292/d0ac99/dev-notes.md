# 开发笔记 — Design bill query API schema and database indexes

> 2026-05-02 01:00 | LLM

## 产出文件
- [backend/schemas/bill.py](/app#repo?file=backend/schemas/bill.py) (2713 chars)
- [backend/database/migrations/add_bill_indexes.sql](/app#repo?file=backend/database/migrations/add_bill_indexes.sql) (1210 chars)
- [backend/routers/bills.py](/app#repo?file=backend/routers/bills.py) (6671 chars)
- [backend/database/connection.py](/app#repo?file=backend/database/connection.py) (2065 chars)
- [backend/main.py](/app#repo?file=backend/main.py) (1315 chars)
- [README.md](/app#repo?file=README.md) (4064 chars)

## 自测: 自测 6/6 通过 ✅

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 6 个文件 |
| 入口文件 | ✅ | 存在 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 6 个文件已落盘 |

## 代码变更 (Diff)

### backend/schemas/bill.py (新建, 2713 chars)
```
+ from pydantic import BaseModel, Field
+ from typing import Optional, Literal
+ from datetime import datetime
+ from decimal import Decimal
+ 
+ 
+ class BillQueryRequest(BaseModel):
+     """Bill query request with multiple filter conditions."""
+     
+     start_date: Optional[str] = Field(
+         None,
+         description="Start date in YYYY-MM-DD format",
+         pattern=r"^\d{4}-\d{2}-\d{2}$"
+     )
+     end_date: Optional[str] = Field(
+         None,
+         description="End date in YYYY-MM-DD format",
+         pattern=r"^\d{4}-\d{2}-\d{2}$"
+     )
+     category: Optional[str] = Field(
+ ... (更多)
```

### backend/database/migrations/add_bill_indexes.sql (新建, 1210 chars)
```
+ -- Add indexes for bill query optimization
+ -- Run this migration to improve query performance
+ 
+ -- Index on date field for time range queries
+ CREATE INDEX IF NOT EXISTS idx_bills_date ON bills(date DESC);
+ 
+ -- Index on category for category filtering
+ CREATE INDEX IF NOT EXISTS idx_bills_category ON bills(category);
+ 
+ -- Index on bill_type for type filtering
+ CREATE INDEX IF NOT EXISTS idx_bills_type ON bills(bill_type);
+ 
+ -- Index on amount for amount range queries
+ CREATE INDEX IF NOT EXISTS idx_bills_amount ON bills(amount);
+ 
+ -- Composite index for common query patterns (type + date)
+ CREATE INDEX IF NOT EXISTS idx_bills_type_date ON bills(bill_type, date DESC);
+ 
+ -- Composite index for category + date queries
+ CREATE INDEX IF NOT EXISTS idx_bills_category_date ON bills(category, date DESC);
+ ... (更多)
```

### backend/routers/bills.py (新建, 6671 chars)
```
+ from fastapi import APIRouter, Depends, HTTPException, Query
+ from typing import Optional
+ import aiosqlite
+ from decimal import Decimal
+ import logging
+ from datetime import datetime
+ 
+ from backend.schemas.bill import (
+     BillQueryRequest,
+     BillQueryResponse,
+     BillItem,
+     BillStatistics
+ )
+ from backend.database.connection import get_db
+ 
+ logger = logging.getLogger(__name__)
+ router = APIRouter(prefix="/api/bills", tags=["bills"])
+ 
+ 
+ @router.get("/query", response_model=BillQueryResponse)
+ ... (更多)
```

### backend/database/connection.py (新建, 2065 chars)
```
+ import aiosqlite
+ import os
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
+ DB_PATH = os.getenv("DB_PATH", "bills.db")
+ 
+ 
+ async def get_db():
+     """
+     Dependency to get database connection.
+     
+     Yields:
+         aiosqlite.Connection: Database connection with row factory set.
+     """
+     async with aiosqlite.connect(DB_PATH, timeout=5.0) as db:
+         db.row_factory = aiosqlite.Row
+         yield db
+ 
+ ... (更多)
```

### backend/main.py (新建, 1315 chars)
```
+ from fastapi import FastAPI
+ from fastapi.middleware.cors import CORSMiddleware
+ import logging
+ import os
+ 
+ from backend.routers import bills
+ from backend.database.connection import init_database
+ 
+ # Configure logging
+ logging.basicConfig(
+     level=logging.INFO,
+     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
+ )
+ logger = logging.getLogger(__name__)
+ 
+ app = FastAPI(
+     title="Bill Management API",
+     description="API for managing personal bills with advanced query capabilities",
+     version="1.0.0"
+ )
+ ... (更多)
```
