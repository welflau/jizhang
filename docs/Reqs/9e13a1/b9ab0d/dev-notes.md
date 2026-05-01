# 开发笔记 — Create budgets table schema and migration

> 2026-05-02 01:05 | LLM

## 产出文件
- [backend/app/models/budget.py](/app#repo?file=backend/app/models/budget.py) (1650 chars)
- [backend/alembic/versions/002_create_budgets_table.py](/app#repo?file=backend/alembic/versions/002_create_budgets_table.py) (2083 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 2 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 2 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/models/budget.py (新建, 1650 chars)
```
+ from datetime import datetime
+ from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index
+ from sqlalchemy.orm import relationship
+ from app.database import Base
+ 
+ 
+ class Budget(Base):
+     __tablename__ = "budgets"
+ 
+     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
+     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
+     category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
+     amount = Column(Numeric(10, 2), nullable=False)
+     period = Column(String(7), nullable=False, comment="预算周期，格式 YYYY-MM")
+     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
+ 
+     # 关系
+     user = relationship("User", back_populates="budgets")
+     category = relationship("Category", back_populates="budgets")
+ 
+ ... (更多)
```

### backend/alembic/versions/002_create_budgets_table.py (新建, 2083 chars)
```
+ """Create budgets table
+ 
+ Revision ID: 002
+ Revises: 001
+ Create Date: 2024-01-01 00:00:00.000000
+ 
+ """
+ from alembic import op
+ import sqlalchemy as sa
+ from sqlalchemy.dialects import postgresql
+ 
+ # revision identifiers, used by Alembic.
+ revision = '002'
+ down_revision = '001'
+ branch_labels = None
+ depends_on = None
+ 
+ 
+ def upgrade():
+     # Create budgets table
+ ... (更多)
```
