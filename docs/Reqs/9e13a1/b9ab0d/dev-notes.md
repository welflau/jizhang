# 开发笔记 — Create budgets table schema and migration

> 2026-05-02 01:06 | LLM

## 产出文件
- [backend/migrations/004_create_budgets_table.sql](/app#repo?file=backend/migrations/004_create_budgets_table.sql) (2510 chars)
- [app/models/budget.py](/app#repo?file=app/models/budget.py) (2269 chars)
- [tests/test_budget_schema.py](/app#repo?file=tests/test_budget_schema.py) (9947 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 3 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 3 个文件已落盘 |

## 代码变更 (Diff)

### backend/migrations/004_create_budgets_table.sql (新建, 2510 chars)
```
+ -- Migration: Create budgets table
+ -- Description: Create budgets table with user_id, category_id, amount, period, and timestamps
+ -- Created: 2024
+ 
+ -- Create budgets table
+ CREATE TABLE IF NOT EXISTS budgets (
+     id BIGSERIAL PRIMARY KEY,
+     user_id BIGINT NOT NULL,
+     category_id BIGINT,
+     amount DECIMAL(15, 2) NOT NULL CHECK (amount >= 0),
+     period VARCHAR(7) NOT NULL CHECK (period ~ '^\d{4}-(0[1-9]|1[0-2])$'),
+     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
+     updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
+     
+     -- Foreign key constraints
+     CONSTRAINT fk_budgets_user_id 
+         FOREIGN KEY (user_id) 
+         REFERENCES users(id) 
+         ON DELETE CASCADE,
+     
+ ... (更多)
```

### app/models/budget.py (新建, 2269 chars)
```
+ from datetime import datetime
+ from app import db
+ 
+ 
+ class Budget(db.Model):
+     __tablename__ = 'budgets'
+ 
+     id = db.Column(db.Integer, primary_key=True)
+     user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
+     category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
+     amount = db.Column(db.Numeric(10, 2), nullable=False)
+     period = db.Column(db.String(7), nullable=False)  # 格式: YYYY-MM
+     created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
+ 
+     # 索引定义
+     __table_args__ = (
+         db.Index('idx_budget_user_id', 'user_id'),
+         db.Index('idx_budget_period', 'period'),
+         db.Index('idx_budget_user_period', 'user_id', 'period'),
+         db.UniqueConstraint('user_id', 'category_id', 'period', name='uq_user_category_period'),
+ ... (更多)
```

### tests/test_budget_schema.py (新建, 9947 chars)
```
+ tests/test_budget_schema.py
+ 
+ import pytest
+ from datetime import datetime
+ from sqlalchemy import create_engine, inspect
+ from sqlalchemy.orm import sessionmaker
+ from app.models.budget import Budget
+ from app.models.user import User
+ from app.models.category import Category
+ from app.database import Base
+ 
+ 
+ @pytest.fixture
+ def engine():
+     """Create test database engine"""
+     engine = create_engine('sqlite:///:memory:')
+     Base.metadata.create_all(engine)
+     return engine
+ 
+ 
+ ... (更多)
```
