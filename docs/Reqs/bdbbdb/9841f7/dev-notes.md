# 开发笔记 — Create categories database table and migration

> 2026-05-02 01:07 | LLM

## 产出文件
- [backend/app/models/category.py](/app#repo?file=backend/app/models/category.py) (1656 chars)
- [backend/alembic/versions/001_create_categories_table.py](/app#repo?file=backend/alembic/versions/001_create_categories_table.py) (2672 chars)
- [backend/alembic/env.py](/app#repo?file=backend/alembic/env.py) (2443 chars)
- [backend/alembic.ini](/app#repo?file=backend/alembic.ini) (3323 chars)

## 自测: 自测 6/6 通过 ✅

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 4 个文件 |
| 入口文件 | ✅ | 存在 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 4 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/models/category.py (新建, 1656 chars)
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

### backend/alembic/versions/001_create_categories_table.py (新建, 2672 chars)
```
+ """create categories table
+ 
+ Revision ID: 001
+ Revises: 
+ Create Date: 2024-01-01 00:00:00.000000
+ 
+ """
+ from alembic import op
+ import sqlalchemy as sa
+ from sqlalchemy.dialects import postgresql
+ 
+ # revision identifiers, used by Alembic.
+ revision = '001'
+ down_revision = None
+ branch_labels = None
+ depends_on = None
+ 
+ 
+ def upgrade() -> None:
+     # Create categories table
+ ... (更多)
```

### backend/alembic/env.py (新建, 2443 chars)
```
+ from logging.config import fileConfig
+ from sqlalchemy import engine_from_config
+ from sqlalchemy import pool
+ from alembic import context
+ import os
+ import sys
+ 
+ # 将项目根目录添加到 Python 路径
+ sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
+ 
+ from app.core.config import settings
+ from app.db.base import Base
+ 
+ # this is the Alembic Config object, which provides
+ # access to the values within the .ini file in use.
+ config = context.config
+ 
+ # 从设置中获取数据库 URL
+ config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
+ 
+ ... (更多)
```

### backend/alembic.ini (新建, 3323 chars)
```
+ # A generic, single database configuration.
+ 
+ [alembic]
+ # path to migration scripts
+ script_location = alembic
+ 
+ # template used to generate migration files
+ # file_template = %%(rev)s_%%(slug)s
+ 
+ # sys.path path, will be prepended to sys.path if present.
+ # defaults to the current working directory.
+ prepend_sys_path = .
+ 
+ # timezone to use when rendering the date within the migration file
+ # as well as the filename.
+ # If specified, requires the python-dateutil library that can be
+ # installed by adding `alembic[tz]` to the pip requirements
+ # string value is passed to dateutil.tz.gettz()
+ # leave blank for localtime
+ # timezone =
+ ... (更多)
```
