# 开发笔记 — Create budgets table schema and migration

> 2026-05-02 00:59 | LLM

## 产出文件
- [backend/migrations/002_create_budgets_table.sql](/app#repo?file=backend/migrations/002_create_budgets_table.sql) (1673 chars)
- [backend/db_migration.py](/app#repo?file=backend/db_migration.py) (4961 chars)
- [backend/models/budget.py](/app#repo?file=backend/models/budget.py) (1598 chars)
- [backend/routes/budgets.py](/app#repo?file=backend/routes/budgets.py) (8955 chars)
- [backend/dependencies.py](/app#repo?file=backend/dependencies.py) (1654 chars)
- [README.md](/app#repo?file=README.md) (4171 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 6 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 6 个文件已落盘 |

## 代码变更 (Diff)

### backend/migrations/002_create_budgets_table.sql (新建, 1673 chars)
```
+ -- Migration: Create budgets table
+ -- Created: 2024-01-01
+ -- Description: Add budgets table with user_id, category_id, amount, period, and timestamps
+ 
+ CREATE TABLE IF NOT EXISTS budgets (
+     id INTEGER PRIMARY KEY AUTOINCREMENT,
+     user_id INTEGER NOT NULL,
+     category_id INTEGER,
+     amount REAL NOT NULL CHECK(amount >= 0),
+     period TEXT NOT NULL CHECK(period GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'),
+     created_at TEXT NOT NULL DEFAULT (datetime('now')),
+     updated_at TEXT NOT NULL DEFAULT (datetime('now')),
+     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
+     FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
+ );
+ 
+ -- Create index on user_id for faster user-specific queries
+ CREATE INDEX IF NOT EXISTS idx_budgets_user_id ON budgets(user_id);
+ 
+ -- Create index on period for faster period-based queries
+ ... (更多)
```

### backend/db_migration.py (新建, 4961 chars)
```
+ #!/usr/bin/env python3
+ """
+ Database Migration Runner
+ 
+ Executes SQL migration files in order to set up or update the database schema.
+ Migrations are stored in backend/migrations/ directory and executed sequentially.
+ """
+ 
+ import aiosqlite
+ import asyncio
+ import os
+ import logging
+ from pathlib import Path
+ 
+ logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
+ logger = logging.getLogger(__name__)
+ 
+ DB_PATH = os.getenv("DB_PATH", "backend/app.db")
+ MIGRATIONS_DIR = Path("backend/migrations")
+ 
+ ... (更多)
```

### backend/models/budget.py (新建, 1598 chars)
```
+ """Budget data models and schemas."""
+ 
+ from pydantic import BaseModel, Field
+ from typing import Optional
+ from datetime import datetime
+ 
+ 
+ class BudgetBase(BaseModel):
+     """Base budget schema with common fields."""
+     category_id: Optional[int] = Field(None, description="Category ID (null for overall budget)")
+     amount: float = Field(ge=0, description="Budget amount (must be non-negative)")
+     period: str = Field(
+         pattern=r"^\d{4}-\d{2}$",
+         description="Budget period in YYYY-MM format",
+         examples=["2024-01", "2024-12"]
+     )
+ 
+ 
+ class CreateBudgetRequest(BudgetBase):
+     """Request schema for creating a new budget."""
+ ... (更多)
```

### backend/routes/budgets.py (新建, 8955 chars)
```
+ """Budget management API routes."""
+ 
+ from fastapi import APIRouter, Depends, HTTPException, status
+ from typing import List, Optional
+ import aiosqlite
+ import logging
+ 
+ from backend.models.budget import (
+     CreateBudgetRequest,
+     UpdateBudgetRequest,
+     BudgetResponse,
+     BudgetWithUsage
+ )
+ from backend.dependencies import get_db, get_current_user
+ 
+ logger = logging.getLogger(__name__)
+ router = APIRouter(prefix="/api/budgets", tags=["budgets"])
+ 
+ 
+ @router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
+ ... (更多)
```

### backend/dependencies.py (新建, 1654 chars)
```
+ """FastAPI dependency injection utilities."""
+ 
+ import aiosqlite
+ import os
+ from typing import AsyncGenerator
+ from fastapi import Header, HTTPException, status
+ 
+ DB_PATH = os.getenv("DB_PATH", "backend/app.db")
+ 
+ 
+ async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
+     """
+     Database connection dependency.
+     
+     Yields:
+         Database connection with foreign keys enabled
+     """
+     async with aiosqlite.connect(DB_PATH) as db:
+         await db.execute("PRAGMA foreign_keys = ON")
+         db.row_factory = aiosqlite.Row
+ ... (更多)
```
