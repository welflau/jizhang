# 开发笔记 — Setup database connection pool and base model

> 2026-05-02 01:23 | LLM

## 产出文件
- [backend/app/models/base.py](/app#repo?file=backend/app/models/base.py) (5369 chars)
- [backend/app/core/deps.py](/app#repo?file=backend/app/core/deps.py) (3715 chars)
- [backend/scripts/init_db.py](/app#repo?file=backend/scripts/init_db.py) (2670 chars)
- [backend/.env.example](/app#repo?file=backend/.env.example) (377 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (1546 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 5 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 5 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/models/base.py (新建, 5369 chars)
```
+ from datetime import datetime
+ from typing import AsyncGenerator
+ 
+ from sqlalchemy import MetaData, create_engine
+ from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
+ from sqlalchemy.ext.declarative import declarative_base
+ from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
+ from sqlalchemy.pool import NullPool, QueuePool
+ 
+ from app.core.config import settings
+ 
+ 
+ # 定义命名约定，用于自动生成约束名称
+ convention = {
+     "ix": "ix_%(column_0_label)s",
+     "uq": "uq_%(table_name)s_%(column_0_name)s",
+     "ck": "ck_%(table_name)s_%(constraint_name)s",
+     "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
+     "pk": "pk_%(table_name)s"
+ }
+ ... (更多)
```

### backend/app/core/deps.py (新建, 3715 chars)
```
+ from typing import AsyncGenerator
+ from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
+ from sqlalchemy.orm import DeclarativeBase
+ from app.core.config import settings
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
+ # 创建异步数据库引擎
+ engine = create_async_engine(
+     settings.DATABASE_URL,
+     echo=settings.DEBUG,
+     pool_size=settings.DB_POOL_SIZE,
+     max_overflow=settings.DB_MAX_OVERFLOW,
+     pool_pre_ping=True,
+     pool_recycle=3600,
+ )
+ 
+ # 创建异步会话工厂
+ AsyncSessionLocal = async_sessionmaker(
+ ... (更多)
```

### backend/scripts/init_db.py (新建, 2670 chars)
```
+ import asyncio
+ import sys
+ from pathlib import Path
+ 
+ # Add project root to Python path
+ project_root = Path(__file__).parent.parent.parent
+ sys.path.insert(0, str(project_root))
+ 
+ from sqlalchemy.ext.asyncio import create_async_engine
+ from app.core.config import settings
+ from app.models.base import Base
+ from app.core.database import engine
+ 
+ 
+ async def init_db():
+     """Initialize database by creating all tables"""
+     print("Starting database initialization...")
+     print(f"Database URL: {settings.DATABASE_URL}")
+     
+     try:
+ ... (更多)
```

### backend/.env.example (新建, 377 chars)
```
+ # Database Configuration
+ DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
+ DATABASE_POOL_SIZE=20
+ DATABASE_MAX_OVERFLOW=10
+ DATABASE_POOL_TIMEOUT=30
+ DATABASE_POOL_RECYCLE=3600
+ DATABASE_ECHO=False
+ 
+ # Application Configuration
+ APP_ENV=development
+ APP_DEBUG=True
+ SECRET_KEY=your-secret-key-here-change-in-production
+ 
+ # Server Configuration
+ HOST=0.0.0.0
+ PORT=8000
```

### backend/app/main.py (修改)
```diff
--- a/backend/app/main.py
+++ b/backend/app/main.py
@@ -1,7 +1,7 @@
 from fastapi import FastAPI

 from fastapi.middleware.cors import CORSMiddleware

 from backend.app.core.config import settings

-from backend.app.core.database import init_db

+from backend.app.core.database import init_db, close_db

 from backend.app.routers import auth

 import logging

 

@@ -38,6 +38,14 @@
     logger.info("Database initialized successfully")

 

 

+@app.on_event("shutdown")

+async def shutdown_event():

+    """Close database connection pool on application shutdown."""

+    logger.info("Closing database connection pool...")

+    await close_db()

+    logger.info("Database connection pool closed successfully")

+

+

 @app.get("/")

 async def root():

     """Health check endpoint."""

```
