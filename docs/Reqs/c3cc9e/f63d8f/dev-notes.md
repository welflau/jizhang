# 开发笔记 — Setup database connection pool and base model

> 2026-05-02 01:26 | LLM

## 产出文件
- [backend/app/core/__init__.py](/app#repo?file=backend/app/core/__init__.py) (216 chars)
- [backend/app/core/config.py](/app#repo?file=backend/app/core/config.py) (2970 chars)
- [backend/app/core/database.py](/app#repo?file=backend/app/core/database.py) (5047 chars)
- [backend/app/db/__init__.py](/app#repo?file=backend/app/db/__init__.py) (6099 chars)
- [backend/app/db/session.py](/app#repo?file=backend/app/db/session.py) (5756 chars)
- [backend/app/db/init_db.py](/app#repo?file=backend/app/db/init_db.py) (4155 chars)
- [backend/alembic.ini](/app#repo?file=backend/alembic.ini) (3520 chars)
- [backend/alembic/env.py](/app#repo?file=backend/alembic/env.py) (2900 chars)
- [backend/.env.example](/app#repo?file=backend/.env.example) (474 chars)
- [backend/main.py](/app#repo?file=backend/main.py) (11980 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 10 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 10 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/core/__init__.py (新建, 216 chars)
```
+ from app.core.config import settings
+ from app.core.database import Base, engine, get_db, init_db, SessionLocal
+ 
+ __all__ = [
+     "settings",
+     "Base",
+     "engine",
+     "get_db",
+     "init_db",
+     "SessionLocal",
+ ]
```

### backend/app/core/config.py (新建, 2970 chars)
```
+ import os
+ from typing import Optional
+ from pydantic_settings import BaseSettings
+ from pydantic import Field, PostgresDsn, validator
+ 
+ 
+ class Settings(BaseSettings):
+     """
+     Application settings with environment variable support
+     """
+     
+     # Application
+     APP_NAME: str = "FastAPI Application"
+     APP_VERSION: str = "1.0.0"
+     DEBUG: bool = Field(default=False, env="DEBUG")
+     
+     # API
+     API_V1_PREFIX: str = "/api/v1"
+     
+     # Database
+ ... (更多)
```

### backend/app/core/database.py (新建, 5047 chars)
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
+ class Base(DeclarativeBase):
+     """Base class for all database models"""
+     pass
+ 
+ 
+ # Create async engine
+ engine = create_async_engine(
+     settings.DATABASE_URL,
+     echo=settings.DATABASE_ECHO,
+     future=True,
+ ... (更多)
```

### backend/app/db/__init__.py (新建, 6099 chars)
```
+ """
+ Database initialization module.
+ Configures database connection pool, session management, and base models.
+ """
+ 
+ from sqlalchemy import create_engine
+ from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
+ from sqlalchemy.orm import declarative_base, sessionmaker
+ from sqlalchemy.pool import NullPool, QueuePool
+ from typing import AsyncGenerator
+ import logging
+ 
+ from app.core.config import settings
+ 
+ # Configure logging
+ logger = logging.getLogger(__name__)
+ 
+ # Create declarative base for models
+ Base = declarative_base()
+ 
+ ... (更多)
```

### backend/app/db/session.py (新建, 5756 chars)
```
+ from sqlalchemy import create_engine
+ from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
+ from sqlalchemy.orm import sessionmaker, Session
+ from sqlalchemy.pool import NullPool, QueuePool
+ from typing import AsyncGenerator, Generator
+ import logging
+ 
+ from app.core.config import settings
+ 
+ logger = logging.getLogger(__name__)
+ 
+ # 同步数据库引擎（用于迁移和初始化）
+ sync_engine = create_engine(
+     settings.SYNC_DATABASE_URL,
+     pool_pre_ping=True,
+     pool_size=settings.DB_POOL_SIZE,
+     max_overflow=settings.DB_MAX_OVERFLOW,
+     pool_recycle=settings.DB_POOL_RECYCLE,
+     echo=settings.DB_ECHO,
+ )
+ ... (更多)
```

### backend/app/db/init_db.py (新建, 4155 chars)
```
+ import logging
+ from sqlalchemy import create_engine, text
+ from sqlalchemy.orm import sessionmaker
+ from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
+ 
+ from app.core.config import settings
+ from app.models.base import Base
+ 
+ logger = logging.getLogger(__name__)
+ 
+ 
+ # 同步引擎（用于初始化和迁移）
+ sync_engine = create_engine(
+     settings.SYNC_DATABASE_URL,
+     pool_pre_ping=True,
+     pool_size=settings.DB_POOL_SIZE,
+     max_overflow=settings.DB_MAX_OVERFLOW,
+     echo=settings.DB_ECHO,
+ )
+ 
+ ... (更多)
```

### backend/alembic.ini (新建, 3520 chars)
```
+ # A generic, single database configuration.
+ 
+ [alembic]
+ # path to migration scripts
+ script_location = alembic
+ 
+ # template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
+ # Uncomment the line below if you want the files to be prepended with date and time
+ # file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
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
+ ... (更多)
```

### backend/alembic/env.py (新建, 2900 chars)
```
+ from logging.config import fileConfig
+ from sqlalchemy import engine_from_config
+ from sqlalchemy import pool
+ from alembic import context
+ import os
+ import sys
+ from pathlib import Path
+ 
+ # 添加项目根目录到 Python 路径
+ BASE_DIR = Path(__file__).resolve().parent.parent.parent
+ sys.path.append(str(BASE_DIR))
+ 
+ # 导入 Base 模型和所有模型类
+ from app.models.base import Base
+ # 导入所有模型以确保它们被注册到 Base.metadata
+ from app.models import *  # noqa
+ 
+ # this is the Alembic Config object, which provides
+ # access to the values within the .ini file in use.
+ config = context.config
+ ... (更多)
```

### backend/.env.example (新建, 474 chars)
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
+ DEBUG=True
+ SECRET_KEY=your-secret-key-here
+ 
+ # Server Configuration
+ HOST=0.0.0.0
+ PORT=8000
+ 
+ # CORS Configuration
+ ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
+ 
+ ... (更多)
```

### backend/main.py (修改)
```diff
--- a/backend/main.py
+++ b/backend/main.py
@@ -2,6 +2,7 @@
 import logging

 from datetime import datetime, timedelta

 from typing import Optional

+from contextlib import asynccontextmanager

 

 import jwt

 from fastapi import FastAPI, HTTPException, Depends, status

@@ -22,18 +23,8 @@
 DB_PATH = os.getenv("DB_PATH", "app.db")

 PORT = int(os.getenv("PORT", "8080"))

 

-app = FastAPI(title="User Auth API")

-

-# CORS configuration

-app.add_middleware(

-    CORSMiddleware,

-    allow_origins=["*"],

-    allow_credentials=True,

-    allow_methods=["*"],

-    allow_headers=["*"],

-)

-

-security = HTTPBearer()

+# Database connection pool

+db_pool = None

 

 

 # Pydantic models

@@ -75,11 +66,56 @@
     message: str

 

 

+# Database connection pool management

+class DatabasePool:

+    def __init__(self, db_path: str, pool_size: int = 10):

+        self.db_path = db_path

+        self.pool_size = pool_size

+        self.connections = []

+        self.available = []

+        

+    async def initialize(self):

+        """Initialize connection pool"""

+        for _ in range(self.pool_size):

+            conn = await aiosqlite.connect(self.db_path)

+            conn.row_factory = aiosqlite.Row

+            self.connections.append(conn)

+            self.available.append(conn)

... (共 131 行变更)
```
