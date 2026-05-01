# 开发笔记 — Create budgets table schema and migration

> 2026-05-02 00:58 | LLM

## 产出文件
- [backend/migrations/002_create_budgets_table.sql](/app#repo?file=backend/migrations/002_create_budgets_table.sql) (1859 chars)
- [backend/migrations/001_init_schema.sql](/app#repo?file=backend/migrations/001_init_schema.sql) (2237 chars)
- [backend/db/migrate.py](/app#repo?file=backend/db/migrate.py) (5058 chars)
- [backend/README.md](/app#repo?file=backend/README.md) (2117 chars)

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

### backend/migrations/002_create_budgets_table.sql (新建, 1859 chars)
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

### backend/migrations/001_init_schema.sql (新建, 2237 chars)
```
+ -- Migration: Initialize database schema
+ -- Description: Create initial tables for users, categories, transactions, and migration tracking
+ -- Author: DevAgent
+ -- Date: 2024
+ 
+ -- Create schema_migrations table to track applied migrations
+ CREATE TABLE IF NOT EXISTS schema_migrations (
+     version VARCHAR(10) PRIMARY KEY,
+     description VARCHAR(255) NOT NULL,
+     applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+ );
+ 
+ -- Create users table
+ CREATE TABLE IF NOT EXISTS users (
+     id INTEGER PRIMARY KEY AUTOINCREMENT,
+     username VARCHAR(50) UNIQUE NOT NULL,
+     email VARCHAR(100) UNIQUE NOT NULL,
+     password_hash VARCHAR(255) NOT NULL,
+     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+ ... (更多)
```

### backend/db/migrate.py (新建, 5058 chars)
```
+ #!/usr/bin/env python3
+ """
+ Database migration runner for SQLite.
+ 
+ Usage:
+     python migrate.py          # Run all pending migrations
+     python migrate.py --reset  # Drop all tables and re-run migrations
+ """
+ 
+ import asyncio
+ import os
+ import sys
+ from pathlib import Path
+ import aiosqlite
+ import logging
+ 
+ logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
+ logger = logging.getLogger(__name__)
+ 
+ # Database configuration
+ ... (更多)
```
