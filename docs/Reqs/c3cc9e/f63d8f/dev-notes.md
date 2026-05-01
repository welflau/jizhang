# 开发笔记 — Setup database connection pool and base model

> 2026-05-02 01:31 | LLM

## 产出文件
- [backend/app/core/config.py](/app#repo?file=backend/app/core/config.py) (605 chars)
- [backend/app/database.py](/app#repo?file=backend/app/database.py) (2234 chars)
- [backend/app/models/base.py](/app#repo?file=backend/app/models/base.py) (171 chars)
- [backend/app/models/__init__.py](/app#repo?file=backend/app/models/__init__.py) (250 chars)
- [backend/app/models/user.py](/app#repo?file=backend/app/models/user.py) (973 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (1801 chars)
- [backend/scripts/init_db.py](/app#repo?file=backend/scripts/init_db.py) (1923 chars)
- [backend/.env.example](/app#repo?file=backend/.env.example) (395 chars)
- [backend/requirements.txt](/app#repo?file=backend/requirements.txt) (151 chars)
- [backend/README.md](/app#repo?file=backend/README.md) (4116 chars)

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

### backend/app/core/config.py (新建, 605 chars)
```
+ from pydantic_settings import BaseSettings
+ from functools import lru_cache
+ import os
+ 
+ 
+ class Settings(BaseSettings):
+     """Application configuration loaded from environment variables."""
+     
+     # Database
+     DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
+     
+     # Server
+     HOST: str = "0.0.0.0"
+     PORT: int = 8080
+     
+     # Application
+     APP_NAME: str = "FastAPI Application"
+     DEBUG: bool = False
+     
+     class Config:
+ ... (更多)
```

### backend/app/database.py (新建, 2234 chars)
```
+ from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
+ from sqlalchemy.pool import NullPool
+ from typing import AsyncGenerator
+ import logging
+ 
+ from app.core.config import get_settings
+ 
+ logger = logging.getLogger(__name__)
+ settings = get_settings()
+ 
+ # Create async engine with connection pool configuration
+ engine = create_async_engine(
+     settings.DATABASE_URL,
+     echo=settings.DEBUG,
+     poolclass=NullPool if "sqlite" in settings.DATABASE_URL else None,
+     pool_size=10 if "sqlite" not in settings.DATABASE_URL else None,
+     max_overflow=20 if "sqlite" not in settings.DATABASE_URL else None,
+     pool_pre_ping=True,
+ )
+ 
+ ... (更多)
```

### backend/app/models/base.py (新建, 171 chars)
```
+ from sqlalchemy.orm import declarative_base
+ 
+ # Create declarative base class for all ORM models
+ # All models should inherit from this Base class
+ Base = declarative_base()
+ 
```

### backend/app/models/__init__.py (新建, 250 chars)
```
+ """Models package.
+ 
+ All SQLAlchemy ORM models should be imported here to ensure
+ they are registered with Base.metadata before database initialization.
+ """
+ 
+ from app.models.base import Base
+ from app.models.user import User
+ 
+ __all__ = ["Base", "User"]
+ 
```

### backend/app/models/user.py (新建, 973 chars)
```
+ from sqlalchemy import Column, Integer, String, DateTime
+ from sqlalchemy.sql import func
+ from app.models.base import Base
+ 
+ 
+ class User(Base):
+     """User model for testing database connection and Base inheritance.
+     
+     This is a minimal test model to verify:
+     1. Base class can be inherited
+     2. Database tables can be created
+     3. SQLAlchemy ORM works correctly
+     """
+     
+     __tablename__ = "users"
+     
+     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
+     username = Column(String(50), unique=True, nullable=False, index=True)
+     email = Column(String(100), unique=True, nullable=False, index=True)
+     created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
+ ... (更多)
```

### backend/app/main.py (修改)
```diff
--- a/backend/app/main.py
+++ b/backend/app/main.py
@@ -1,53 +1,79 @@
 from fastapi import FastAPI

-from fastapi.middleware.cors import CORSMiddleware

 from contextlib import asynccontextmanager

+import logging

 import os

 

-from .database import init_db, close_db

-from .routers import auth

+from app.core.config import get_settings

+from app.database import init_db, close_db

+

+# Configure logging

+logging.basicConfig(

+    level=logging.INFO,

+    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

+)

+logger = logging.getLogger(__name__)

+

+settings = get_settings()

 

 

 @asynccontextmanager

 async def lifespan(app: FastAPI):

-    """Application lifespan manager."""

-    # Startup: initialize database

-    await init_db()

+    """Application lifespan manager.

+    

+    Handles startup and shutdown events:

+    - Startup: Initialize database connection and create tables

+    - Shutdown: Close database connections gracefully

+    """

+    # Startup

+    logger.info(f"Starting {settings.APP_NAME}...")

+    try:

+        await init_db()

+        logger.info("Database connection pool initialized")

+    except Exception as e:

+        logger.error(f"Failed to initialize database: {e}")

+        raise

+    

     yield

-    # Shutdown: cleanup if needed

+    

+    # Shutdown

+    logger.info("Shutting down application...")

     await close_db()

... (共 111 行变更)
```

### backend/scripts/init_db.py (新建, 1923 chars)
```
+ #!/usr/bin/env python3
+ """Database initialization script.
+ 
+ This script creates all database tables defined in models.
+ Run this script manually to initialize or reset the database:
+ 
+     python scripts/init_db.py
+ """
+ 
+ import asyncio
+ import sys
+ from pathlib import Path
+ 
+ # Add parent directory to path to import app modules
+ sys.path.insert(0, str(Path(__file__).parent.parent))
+ 
+ from app.database import init_db, close_db, engine
+ from app.models.base import Base
+ from app.core.config import get_settings
+ import logging
+ ... (更多)
```

### backend/.env.example (新建, 395 chars)
```
+ # Database Configuration
+ # SQLite (default for development)
+ DATABASE_URL=sqlite+aiosqlite:///./app.db
+ 
+ # PostgreSQL (production)
+ # DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
+ 
+ # MySQL
+ # DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/dbname
+ 
+ # Server Configuration
+ HOST=0.0.0.0
+ PORT=8080
+ 
+ # Application Configuration
+ APP_NAME=FastAPI Application
+ DEBUG=False
+ 
```
