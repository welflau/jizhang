# 开发笔记 — Create categories database table and migration

> 2026-05-02 01:13 | LLM

## 产出文件
- [backend/app/models/category.py](/app#repo?file=backend/app/models/category.py) (1598 chars)
- [backend/alembic/versions/004_create_categories_table.py](/app#repo?file=backend/alembic/versions/004_create_categories_table.py) (2677 chars)
- [backend/tests/test_category_migration.py](/app#repo?file=backend/tests/test_category_migration.py) (8371 chars)

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

### backend/app/models/category.py (新建, 1598 chars)
```
+ from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index, Enum as SQLEnum
+ from sqlalchemy.orm import relationship
+ from app.database import Base
+ import enum
+ 
+ 
+ class CategoryType(str, enum.Enum):
+     income = "income"
+     expense = "expense"
+ 
+ 
+ class Category(Base):
+     __tablename__ = "categories"
+ 
+     id = Column(Integer, primary_key=True, index=True)
+     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
+     name = Column(String(50), nullable=False)
+     type = Column(SQLEnum(CategoryType), nullable=False)
+     icon = Column(String(50), nullable=True)
+     color = Column(String(20), nullable=True)
+ ... (更多)
```

### backend/alembic/versions/004_create_categories_table.py (新建, 2677 chars)
```
+ """create categories table
+ 
+ Revision ID: 004
+ Revises: 003
+ Create Date: 2024-01-01 00:00:00.000000
+ 
+ """
+ from alembic import op
+ import sqlalchemy as sa
+ from sqlalchemy.dialects import postgresql
+ 
+ # revision identifiers, used by Alembic.
+ revision = '004'
+ down_revision = '003'
+ branch_labels = None
+ depends_on = None
+ 
+ 
+ def upgrade():
+     # Create categories table
+ ... (更多)
```

### backend/tests/test_category_migration.py (新建, 8371 chars)
```
+ import pytest
+ from sqlalchemy import inspect, Index
+ from backend.app.models.category import Category
+ from backend.app.core.database import Base, engine
+ 
+ 
+ class TestCategoryMigration:
+     """测试 Category 表结构和迁移"""
+ 
+     def test_category_table_exists(self):
+         """测试 categories 表是否存在"""
+         inspector = inspect(engine)
+         tables = inspector.get_table_names()
+         assert 'categories' in tables, "categories 表不存在"
+ 
+     def test_category_table_columns(self):
+         """测试 categories 表的列结构"""
+         inspector = inspect(engine)
+         columns = inspector.get_columns('categories')
+         column_names = [col['name'] for col in columns]
+ ... (更多)
```
