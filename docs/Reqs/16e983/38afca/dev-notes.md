# 开发笔记 — 用户注册与登录系统

> 2026-05-02 01:01 | LLM

## 产出文件
- [backend/app/models/user.py](/app#repo?file=backend/app/models/user.py) (768 chars)
- [backend/app/core/database.py](/app#repo?file=backend/app/core/database.py) (862 chars)
- [backend/app/core/config.py](/app#repo?file=backend/app/core/config.py) (1184 chars)
- [backend/app/core/security.py](/app#repo?file=backend/app/core/security.py) (2478 chars)
- [backend/app/schemas/auth.py](/app#repo?file=backend/app/schemas/auth.py) (1165 chars)
- [backend/app/routers/auth.py](/app#repo?file=backend/app/routers/auth.py) (5438 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (1274 chars)
- [frontend/index.html](/app#repo?file=frontend/index.html) (19903 chars)
- [tests/test_auth_register.py](/app#repo?file=tests/test_auth_register.py) (2813 chars)
- [tests/test_auth_login.py](/app#repo?file=tests/test_auth_login.py) (2393 chars)
- [requirements.txt](/app#repo?file=requirements.txt) (251 chars)
- [.env.example](/app#repo?file=.env.example) (344 chars)
- [.gitignore](/app#repo?file=.gitignore) (503 chars)
- [README.md](/app#repo?file=README.md) (2726 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 14 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 14 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/models/user.py (新建, 768 chars)
```
+ from sqlalchemy import Column, Integer, String, DateTime
+ from sqlalchemy.sql import func
+ from backend.app.core.database import Base
+ 
+ 
+ class User(Base):
+     """User model for authentication system.
+     
+     Attributes:
+         id: Primary key
+         email: Unique email address for login
+         hashed_password: bcrypt hashed password
+         created_at: Timestamp of account creation
+     """
+     __tablename__ = "users"
+ 
+     id = Column(Integer, primary_key=True, index=True)
+     email = Column(String(255), unique=True, index=True, nullable=False)
+     hashed_password = Column(String(255), nullable=False)
+     created_at = Column(DateTime(timezone=True), server_default=func.now())
+ ... (更多)
```

### backend/app/core/database.py (新建, 862 chars)
```
+ from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
+ from sqlalchemy.orm import declarative_base, sessionmaker
+ from backend.app.core.config import settings
+ 
+ engine = create_async_engine(
+     settings.DATABASE_URL,
+     echo=settings.DEBUG,
+     future=True
+ )
+ 
+ AsyncSessionLocal = sessionmaker(
+     engine,
+     class_=AsyncSession,
+     expire_on_commit=False
+ )
+ 
+ Base = declarative_base()
+ 
+ 
+ async def get_db():
+ ... (更多)
```

### backend/app/core/config.py (新建, 1184 chars)
```
+ from pydantic_settings import BaseSettings
+ from functools import lru_cache
+ import os
+ 
+ 
+ class Settings(BaseSettings):
+     """Application configuration loaded from environment variables.
+     
+     Security-sensitive values (JWT_SECRET_KEY) must be set via env vars.
+     """
+     # Application
+     APP_NAME: str = "User Auth System"
+     DEBUG: bool = False
+     
+     # Database
+     DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
+     
+     # Security
+     JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
+     JWT_ALGORITHM: str = "HS256"
+ ... (更多)
```

### backend/app/core/security.py (新建, 2478 chars)
```
+ from passlib.context import CryptContext
+ from datetime import datetime, timedelta
+ from jose import JWTError, jwt
+ from backend.app.core.config import settings
+ from typing import Optional
+ 
+ pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
+ 
+ 
+ def hash_password(password: str) -> str:
+     """Hash a plain password using bcrypt.
+     
+     Args:
+         password: Plain text password
+         
+     Returns:
+         Hashed password string
+     """
+     return pwd_context.hash(password)
+ 
+ ... (更多)
```

### backend/app/schemas/auth.py (新建, 1165 chars)
```
+ from pydantic import BaseModel, EmailStr, Field
+ from datetime import datetime
+ 
+ 
+ class RegisterRequest(BaseModel):
+     """Request schema for user registration."""
+     email: EmailStr = Field(description="User email address")
+     password: str = Field(min_length=8, max_length=100, description="Password (min 8 chars)")
+ 
+ 
+ class LoginRequest(BaseModel):
+     """Request schema for user login."""
+     email: EmailStr
+     password: str
+     remember_me: bool = False
+ 
+ 
+ class TokenResponse(BaseModel):
+     """Response schema for authentication tokens."""
+     access_token: str
+ ... (更多)
```

### backend/app/routers/auth.py (新建, 5438 chars)
```
+ from fastapi import APIRouter, Depends, HTTPException, status
+ from sqlalchemy.ext.asyncio import AsyncSession
+ from sqlalchemy import select
+ from backend.app.core.database import get_db
+ from backend.app.core.security import (
+     hash_password,
+     verify_password,
+     create_access_token,
+     create_refresh_token,
+     decode_token
+ )
+ from backend.app.models.user import User
+ from backend.app.schemas.auth import (
+     RegisterRequest,
+     LoginRequest,
+     TokenResponse,
+     UserResponse,
+     MessageResponse,
+     PasswordResetRequest
+ )
+ ... (更多)
```

### backend/app/main.py (新建, 1274 chars)
```
+ from fastapi import FastAPI
+ from fastapi.middleware.cors import CORSMiddleware
+ from backend.app.core.config import settings
+ from backend.app.core.database import init_db
+ from backend.app.routers import auth
+ import logging
+ 
+ # Configure logging
+ logging.basicConfig(
+     level=logging.INFO,
+     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
+ )
+ logger = logging.getLogger(__name__)
+ 
+ app = FastAPI(
+     title=settings.APP_NAME,
+     debug=settings.DEBUG
+ )
+ 
+ # CORS middleware for frontend access
+ ... (更多)
```

### frontend/index.html (新建, 19903 chars)
```
+ <!DOCTYPE html>
+ <html lang="en">
+ <head>
+     <meta charset="UTF-8">
+     <meta name="viewport" content="width=device-width, initial-scale=1.0">
+     <title>User Authentication System</title>
+     <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
+     <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
+     <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
+     <style>
+         * {
+             box-sizing: border-box;
+             margin: 0;
+             padding: 0;
+         }
+ 
+         :root {
+             --primary: #1a73e8;
+             --primary-dark: #1557b0;
+             --error: #d93025;
+ ... (更多)
```

### tests/test_auth_register.py (新建, 2813 chars)
```
+ import pytest
+ from httpx import AsyncClient
+ from backend.app.main import app
+ from backend.app.core.database import init_db, engine, Base
+ import os
+ 
+ # Use test database
+ TEST_DB = "test_app.db"
+ 
+ 
+ @pytest.fixture(scope="function")
+ async def test_db():
+     """Create test database for each test."""
+     # Override database URL for testing
+     os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///./{TEST_DB}"
+     
+     # Create tables
+     async with engine.begin() as conn:
+         await conn.run_sync(Base.metadata.create_all)
+     
+ ... (更多)
```

### tests/test_auth_login.py (新建, 2393 chars)
```
+ import pytest
+ from httpx import AsyncClient
+ from backend.app.main import app
+ from backend.app.core.database import engine, Base
+ import os
+ 
+ TEST_DB = "test_app.db"
+ 
+ 
+ @pytest.fixture(scope="function")
+ async def test_db():
+     """Create test database."""
+     os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///./{TEST_DB}"
+     
+     async with engine.begin() as conn:
+         await conn.run_sync(Base.metadata.create_all)
+     
+     yield
+     
+     async with engine.begin() as conn:
+ ... (更多)
```

### .env.example (新建, 344 chars)
```
+ # Application Settings
+ APP_NAME=User Auth System
+ DEBUG=false
+ 
+ # Database
+ DATABASE_URL=sqlite+aiosqlite:///./app.db
+ 
+ # Security (REQUIRED - generate with: openssl rand -hex 32)
+ JWT_SECRET_KEY=your-secret-key-here-change-in-production
+ JWT_ALGORITHM=HS256
+ ACCESS_TOKEN_EXPIRE_MINUTES=30
+ REFRESH_TOKEN_EXPIRE_DAYS=7
+ 
+ # Server
+ HOST=0.0.0.0
+ PORT=8000
```

### .gitignore (新建, 503 chars)
```
+ # Python
+ __pycache__/
+ *.py[cod]
+ *$py.class
+ *.so
+ .Python
+ build/
+ develop-eggs/
+ dist/
+ downloads/
+ eggs/
+ .eggs/
+ lib/
+ lib64/
+ parts/
+ sdist/
+ var/
+ wheels/
+ *.egg-info/
+ .installed.cfg
+ ... (更多)
```
