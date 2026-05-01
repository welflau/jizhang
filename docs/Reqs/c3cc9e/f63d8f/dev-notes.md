# 开发笔记 — Setup database connection pool and base model

> 2026-05-02 01:29 | LLM

## 产出文件
- [backend/app/models/base.py](/app#repo?file=backend/app/models/base.py) (4286 chars)
- [backend/scripts/init_db.py](/app#repo?file=backend/scripts/init_db.py) (2723 chars)
- [backend/.env.example](/app#repo?file=backend/.env.example) (377 chars)
- [backend/tests/test_database.py](/app#repo?file=backend/tests/test_database.py) (8268 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (1155 chars)

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

### backend/app/models/base.py (新建, 4286 chars)
```
+ from typing import AsyncGenerator
+ from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
+ from sqlalchemy.orm import DeclarativeBase
+ from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
+ from app.core.config import settings
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
+ 
+ # 创建异步数据库引擎
+ engine = create_async_engine(
+     settings.DATABASE_URL,
+     echo=settings.DATABASE_ECHO,
+     future=True,
+     pool_pre_ping=True,
+     pool_size=settings.DATABASE_POOL_SIZE,
+     max_overflow=settings.DATABASE_MAX_OVERFLOW,
+     pool_recycle=settings.DATABASE_POOL_RECYCLE,
+     poolclass=AsyncAdaptedQueuePool if settings.DATABASE_POOL_SIZE > 0 else NullPool,
+ ... (更多)
```

### backend/scripts/init_db.py (新建, 2723 chars)
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

### backend/tests/test_database.py (新建, 8268 chars)
```
+ import pytest
+ import asyncio
+ from sqlalchemy import text, select
+ from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
+ from app.core.database import (
+     get_db,
+     init_db,
+     close_db,
+     engine,
+     async_session_maker,
+     Base
+ )
+ from app.core.config import settings
+ from app.models.base import BaseModel
+ 
+ 
+ class TestDatabaseConnection:
+     """测试数据库连接"""
+ 
+     @pytest.mark.asyncio
+ ... (更多)
```

### backend/app/main.py (修改)
```diff
--- a/backend/app/main.py
+++ b/backend/app/main.py
@@ -3,7 +3,7 @@
 from contextlib import asynccontextmanager

 import os

 

-from .database import init_db

+from .database import init_db, close_db

 from .routers import auth

 

 

@@ -14,6 +14,7 @@
     await init_db()

     yield

     # Shutdown: cleanup if needed

+    await close_db()

 

 

 app = FastAPI(

@@ -49,4 +50,4 @@
         host="0.0.0.0",

         port=port,

         reload=True

-    )

+    )
```
