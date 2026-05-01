# 开发笔记 — Create budgets table schema and migration

> 2026-05-02 00:59 | LLM

## 产出文件
- [backend/migrations/002_create_budgets_table.sql](/app#repo?file=backend/migrations/002_create_budgets_table.sql) (1738 chars)
- [backend/migrations/run_migrations.py](/app#repo?file=backend/migrations/run_migrations.py) (3703 chars)
- [backend/models/budget.py](/app#repo?file=backend/models/budget.py) (6843 chars)
- [backend/README.md](/app#repo?file=backend/README.md) (2774 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 4 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 4 个文件已落盘 |

## 代码变更 (Diff)

### backend/migrations/002_create_budgets_table.sql (新建, 1738 chars)
```
+ -- Migration: Create budgets table
+ -- Description: Add budgets table with user_id, category_id, amount, period, and timestamps
+ -- Author: DevAgent
+ -- Date: 2024
+ 
+ -- Create budgets table
+ CREATE TABLE IF NOT EXISTS budgets (
+     id INTEGER PRIMARY KEY AUTOINCREMENT,
+     user_id INTEGER NOT NULL,
+     category_id INTEGER,
+     amount DECIMAL(10, 2) NOT NULL CHECK(amount >= 0),
+     period VARCHAR(7) NOT NULL CHECK(period GLOB '[0-9][0-9][0-9][0-9]-[0-1][0-9]'),
+     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
+     FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
+ );
+ 
+ -- Create index on user_id for faster user-specific queries
+ CREATE INDEX IF NOT EXISTS idx_budgets_user_id ON budgets(user_id);
+ ... (更多)
```

### backend/migrations/run_migrations.py (新建, 3703 chars)
```
+ #!/usr/bin/env python3
+ """Database migration runner for SQLite.
+ 
+ Executes SQL migration files in order and tracks applied migrations.
+ """
+ 
+ import asyncio
+ import aiosqlite
+ import os
+ import sys
+ from pathlib import Path
+ import logging
+ 
+ logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
+ logger = logging.getLogger(__name__)
+ 
+ DB_PATH = os.getenv("DB_PATH", "app.db")
+ MIGRATIONS_DIR = Path(__file__).parent
+ 
+ 
+ ... (更多)
```

### backend/models/budget.py (新建, 6843 chars)
```
+ """Budget data model and database operations.
+ 
+ Handles budget CRUD operations with SQLite async support.
+ """
+ 
+ from typing import Optional, List
+ from datetime import datetime
+ import aiosqlite
+ from pydantic import BaseModel, Field, field_validator
+ import re
+ 
+ 
+ class BudgetCreate(BaseModel):
+     """Schema for creating a new budget."""
+     user_id: int = Field(gt=0, description="User ID who owns this budget")
+     category_id: Optional[int] = Field(None, gt=0, description="Category ID (null for total budget)")
+     amount: float = Field(ge=0, description="Budget amount")
+     period: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="Budget period in YYYY-MM format")
+     
+     @field_validator('period')
+ ... (更多)
```
