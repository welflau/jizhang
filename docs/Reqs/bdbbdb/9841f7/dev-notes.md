# 开发笔记 — Create categories database table and migration

> 2026-05-02 01:07 | LLM

## 产出文件
- [backend/database/__init__.py](/app#repo?file=backend/database/__init__.py) (848 chars)
- [backend/database/migrations/001_create_categories.sql](/app#repo?file=backend/database/migrations/001_create_categories.sql) (1597 chars)
- [backend/database/migration_runner.py](/app#repo?file=backend/database/migration_runner.py) (5732 chars)
- [backend/database/schema.py](/app#repo?file=backend/database/schema.py) (1337 chars)
- [backend/main.py](/app#repo?file=backend/main.py) (1672 chars)
- [backend/tests/test_categories_migration.py](/app#repo?file=backend/tests/test_categories_migration.py) (6447 chars)
- [backend/requirements.txt](/app#repo?file=backend/requirements.txt) (152 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 7 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 7 个文件已落盘 |

## 代码变更 (Diff)

### backend/database/__init__.py (新建, 848 chars)
```
+ """Database initialization and connection management."""
+ import os
+ import aiosqlite
+ from pathlib import Path
+ 
+ DB_PATH = os.getenv("DB_PATH", "app.db")
+ 
+ 
+ async def get_db_connection() -> aiosqlite.Connection:
+     """Get database connection with optimized settings.
+     
+     Returns:
+         aiosqlite.Connection: Configured database connection
+     """
+     db = await aiosqlite.connect(DB_PATH)
+     db.row_factory = aiosqlite.Row
+     await db.execute("PRAGMA foreign_keys = ON")
+     await db.execute("PRAGMA busy_timeout = 5000")
+     return db
+ 
+ ... (更多)
```

### backend/database/migrations/001_create_categories.sql (新建, 1597 chars)
```
+ -- Migration: Create categories table
+ -- Version: 001
+ -- Description: Creates categories table with proper constraints and indexes
+ -- Business rules:
+ --   1. Each category belongs to a user (foreign key to users table)
+ --   2. Type must be either 'income' or 'expense' (CHECK constraint)
+ --   3. Each user can have only ONE default category per type (partial unique index)
+ --   4. Deleting a user cascades to their categories
+ 
+ -- Create categories table
+ CREATE TABLE IF NOT EXISTS categories (
+     id INTEGER PRIMARY KEY AUTOINCREMENT,
+     user_id INTEGER NOT NULL,
+     name TEXT NOT NULL,
+     type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
+     icon TEXT,
+     color TEXT,
+     is_default INTEGER NOT NULL DEFAULT 0 CHECK(is_default IN (0, 1)),
+     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+     FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
+ ... (更多)
```

### backend/database/migration_runner.py (新建, 5732 chars)
```
+ """Database migration runner with version tracking."""
+ import aiosqlite
+ import logging
+ from pathlib import Path
+ from typing import List, Tuple
+ 
+ logger = logging.getLogger(__name__)
+ 
+ MIGRATIONS_DIR = Path(__file__).parent / "migrations"
+ 
+ 
+ async def get_current_version(db: aiosqlite.Connection) -> int:
+     """Get current schema version from database.
+     
+     Args:
+         db: Database connection
+         
+     Returns:
+         int: Current schema version (0 if no migrations table exists)
+     """
+ ... (更多)
```

### backend/database/schema.py (新建, 1337 chars)
```
+ """Database schema definitions for reference.
+ 
+ These constants document the expected table structures.
+ Actual tables are created via migration scripts.
+ """
+ 
+ # Categories table DDL (for reference only - created by migration)
+ CATEGORIES_TABLE_DDL = """
+ CREATE TABLE categories (
+     id INTEGER PRIMARY KEY AUTOINCREMENT,
+     user_id INTEGER NOT NULL,
+     name TEXT NOT NULL,
+     type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
+     icon TEXT,
+     color TEXT,
+     is_default INTEGER NOT NULL DEFAULT 0 CHECK(is_default IN (0, 1)),
+     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+     FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
+ )
+ """
+ ... (更多)
```

### backend/main.py (新建, 1672 chars)
```
+ """FastAPI application entry point."""
+ import os
+ import logging
+ from fastapi import FastAPI
+ from fastapi.middleware.cors import CORSMiddleware
+ from contextlib import asynccontextmanager
+ 
+ from database import init_db
+ 
+ # Configure logging
+ logging.basicConfig(
+     level=logging.INFO,
+     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
+ )
+ logger = logging.getLogger(__name__)
+ 
+ 
+ @asynccontextmanager
+ async def lifespan(app: FastAPI):
+     """Application lifespan manager - runs on startup and shutdown."""
+ ... (更多)
```

### backend/tests/test_categories_migration.py (新建, 6447 chars)
```
+ """Test categories table migration and constraints."""
+ import pytest
+ import aiosqlite
+ import os
+ from pathlib import Path
+ import sys
+ 
+ # Add backend to path
+ sys.path.insert(0, str(Path(__file__).parent.parent))
+ 
+ from database.migration_runner import run_migrations, get_current_version
+ 
+ TEST_DB = "test_categories.db"
+ 
+ 
+ @pytest.fixture
+ async def db():
+     """Create test database and run migrations."""
+     # Clean up any existing test db
+     if os.path.exists(TEST_DB):
+ ... (更多)
```
