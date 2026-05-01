# 开发笔记 — Design transaction data model and database schema

> 2026-05-02 01:00 | LLM

## 产出文件
- [backend/models/transaction.py](/app#repo?file=backend/models/transaction.py) (1446 chars)
- [backend/migrations/001_create_transactions_table.sql](/app#repo?file=backend/migrations/001_create_transactions_table.sql) (1636 chars)
- [backend/migrations/run_migrations.py](/app#repo?file=backend/migrations/run_migrations.py) (2375 chars)
- [backend/database.py](/app#repo?file=backend/database.py) (1207 chars)
- [backend/repositories/transaction_repository.py](/app#repo?file=backend/repositories/transaction_repository.py) (7591 chars)
- [tests/test_transaction_repository.py](/app#repo?file=tests/test_transaction_repository.py) (5184 chars)

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

### backend/models/transaction.py (新建, 1446 chars)
```
+ from pydantic import BaseModel, Field
+ from typing import Optional, Literal
+ from datetime import datetime
+ 
+ 
+ class TransactionBase(BaseModel):
+     """Base transaction schema with common fields."""
+     type: Literal["income", "expense"] = Field(description="Transaction type: income or expense")
+     amount: float = Field(gt=0, description="Transaction amount, must be positive")
+     category_id: int = Field(ge=1, description="Category ID reference")
+     date: datetime = Field(description="Transaction date")
+     note: Optional[str] = Field(None, max_length=500, description="Optional note")
+     payment_method: Optional[str] = Field(None, max_length=50, description="Payment method (cash, card, etc.)")
+ 
+ 
+ class TransactionCreate(TransactionBase):
+     """Schema for creating a new transaction."""
+     pass
+ 
+ 
+ ... (更多)
```

### backend/migrations/001_create_transactions_table.sql (新建, 1636 chars)
```
+ -- Migration: Create transactions table with indexes
+ -- Created: 2024
+ -- Description: Initial transaction data model with optimized indexes for common queries
+ 
+ CREATE TABLE IF NOT EXISTS transactions (
+     id INTEGER PRIMARY KEY AUTOINCREMENT,
+     user_id INTEGER NOT NULL,
+     type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
+     amount REAL NOT NULL CHECK(amount > 0),
+     category_id INTEGER NOT NULL,
+     date TEXT NOT NULL,  -- ISO8601 format: YYYY-MM-DD HH:MM:SS
+     note TEXT,
+     payment_method TEXT,
+     created_at TEXT NOT NULL DEFAULT (datetime('now')),
+     updated_at TEXT NOT NULL DEFAULT (datetime('now')),
+     
+     -- Foreign key constraints (enforced if users/categories tables exist)
+     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
+     FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
+ );
+ ... (更多)
```

### backend/migrations/run_migrations.py (新建, 2375 chars)
```
+ """Database migration runner for SQLite."""
+ import aiosqlite
+ import os
+ import logging
+ from pathlib import Path
+ 
+ logger = logging.getLogger(__name__)
+ 
+ MIGRATIONS_DIR = Path(__file__).parent
+ DB_PATH = os.getenv("DB_PATH", "app.db")
+ 
+ 
+ async def run_migrations():
+     """Execute all SQL migration files in order."""
+     migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
+     
+     if not migration_files:
+         logger.info("No migration files found")
+         return
+     
+ ... (更多)
```

### backend/database.py (新建, 1207 chars)
```
+ """Database connection and initialization."""
+ import aiosqlite
+ import os
+ import logging
+ from contextlib import asynccontextmanager
+ 
+ logger = logging.getLogger(__name__)
+ 
+ DB_PATH = os.getenv("DB_PATH", "app.db")
+ BUSY_TIMEOUT = 5000  # 5 seconds
+ 
+ 
+ @asynccontextmanager
+ async def get_db():
+     """Async context manager for database connections.
+     
+     Yields:
+         aiosqlite.Connection: Database connection with foreign keys enabled
+     """
+     conn = await aiosqlite.connect(DB_PATH, timeout=BUSY_TIMEOUT)
+ ... (更多)
```

### backend/repositories/transaction_repository.py (新建, 7591 chars)
```
+ """Repository layer for transaction data access."""
+ import aiosqlite
+ from typing import List, Optional
+ from datetime import datetime
+ from backend.models.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
+ 
+ class TransactionRepository:
+     """Data access layer for transactions table."""
+     
+     @staticmethod
+     async def create(db: aiosqlite.Connection, user_id: int, data: TransactionCreate) -> TransactionResponse:
+         """Create a new transaction record.
+         
+         Args:
+             db: Database connection
+             user_id: User ID who owns the transaction
+ ... (更多)
```

### tests/test_transaction_repository.py (新建, 5184 chars)
```
+ """Unit tests for transaction repository."""
+ import pytest
+ import aiosqlite
+ from datetime import datetime, timedelta
+ from backend.models.transaction import TransactionCreate, TransactionUpdate
+ from backend.repositories.transaction_repository import TransactionRepository
+ import os
+ import tempfile
+ 
+ 
+ @pytest.fixture
+ async def test_db():
+     """Create a temporary test database."""
+     # Create temp db file
+     fd, db_path = tempfile.mkstemp(suffix=".db")
+     os.close(fd)
+     
+     conn = await aiosqlite.connect(db_path)
+     conn.row_factory = aiosqlite.Row
+     
+ ... (更多)
```
