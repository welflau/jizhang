# 开发笔记 — 用户信息更新 API 开发

> 2026-05-02 01:07 | LLM

## 产出文件
- [backend/models/user.py](/app#repo?file=backend/models/user.py) (1922 chars)
- [backend/schemas/user.py](/app#repo?file=backend/schemas/user.py) (2475 chars)
- [backend/services/user_service.py](/app#repo?file=backend/services/user_service.py) (5059 chars)
- [backend/controllers/user_controller.py](/app#repo?file=backend/controllers/user_controller.py) (2115 chars)
- [backend/middleware/auth.py](/app#repo?file=backend/middleware/auth.py) (2468 chars)
- [backend/main.py](/app#repo?file=backend/main.py) (1609 chars)
- [backend/database.py](/app#repo?file=backend/database.py) (707 chars)
- [tests/test_user_service.py](/app#repo?file=tests/test_user_service.py) (5464 chars)
- [requirements.txt](/app#repo?file=requirements.txt) (222 chars)
- [README.md](/app#repo?file=README.md) (3918 chars)

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

### backend/models/user.py (新建, 1922 chars)
```
+ from sqlalchemy import Column, Integer, String, DateTime, Text
+ from sqlalchemy.sql import func
+ from backend.database import Base
+ import json
+ 
+ class User(Base):
+     """User model with profile and preferences support"""
+     __tablename__ = "users"
+ 
+     id = Column(Integer, primary_key=True, index=True)
+     username = Column(String(50), unique=True, nullable=False, index=True)
+     email = Column(String(100), unique=True, nullable=False, index=True)
+     password_hash = Column(String(255), nullable=False)
+     nickname = Column(String(100), nullable=True)
+     avatar_url = Column(String(500), nullable=True)
+     preferences = Column(Text, nullable=True, default="{}")
+     created_at = Column(DateTime(timezone=True), server_default=func.now())
+     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
+ 
+     def get_preferences(self) -> dict:
+ ... (更多)
```

### backend/schemas/user.py (新建, 2475 chars)
```
+ from pydantic import BaseModel, Field, field_validator
+ from typing import Optional, Dict, Any
+ import re
+ 
+ class UpdateUserInfoRequest(BaseModel):
+     """Request schema for updating user information"""
+     nickname: Optional[str] = Field(None, min_length=1, max_length=100, description="User nickname")
+     avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")
+     current_password: Optional[str] = Field(None, min_length=6, description="Current password for verification")
+     new_password: Optional[str] = Field(None, min_length=6, max_length=128, description="New password")
+     preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences as JSON object")
+ 
+     @field_validator("nickname")
+     @classmethod
+     def validate_nickname(cls, v: Optional[str]) -> Optional[str]:
+         if v is not None:
+             v = v.strip()
+             if not v:
+                 raise ValueError("nickname cannot be empty or whitespace only")
+             if len(v) > 100:
+ ... (更多)
```

### backend/services/user_service.py (新建, 5059 chars)
```
+ from sqlalchemy.ext.asyncio import AsyncSession
+ from sqlalchemy import select
+ from backend.models.user import User
+ from backend.schemas.user import UpdateUserInfoRequest
+ from fastapi import HTTPException
+ import bcrypt
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
+ class UserService:
+     """Service layer for user operations"""
+ 
+     @staticmethod
+     async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
+         """Get user by ID
+         
+         Args:
+             db: Database session
+             user_id: User ID
+ ... (更多)
```

### backend/controllers/user_controller.py (新建, 2115 chars)
```
+ from fastapi import APIRouter, Depends, HTTPException
+ from sqlalchemy.ext.asyncio import AsyncSession
+ from backend.database import get_db
+ from backend.schemas.user import UpdateUserInfoRequest, UserResponse
+ from backend.services.user_service import UserService
+ from backend.middleware.auth import get_current_user
+ from backend.models.user import User
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
+ router = APIRouter(prefix="/api/users", tags=["users"])
+ 
+ @router.put("/me", response_model=UserResponse)
+ async def update_user_info(
+     update_data: UpdateUserInfoRequest,
+     current_user: User = Depends(get_current_user),
+     db: AsyncSession = Depends(get_db)
+ ):
+     """Update current user information
+ ... (更多)
```

### backend/middleware/auth.py (新建, 2468 chars)
```
+ from fastapi import Depends, HTTPException, status
+ from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
+ from sqlalchemy.ext.asyncio import AsyncSession
+ from sqlalchemy import select
+ from backend.database import get_db
+ from backend.models.user import User
+ import jwt
+ import os
+ from datetime import datetime, timedelta
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
+ security = HTTPBearer()
+ 
+ SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
+ ALGORITHM = "HS256"
+ ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
+ 
+ def create_access_token(user_id: int) -> str:
+ ... (更多)
```

### backend/main.py (新建, 1609 chars)
```
+ from fastapi import FastAPI
+ from fastapi.middleware.cors import CORSMiddleware
+ from fastapi.responses import JSONResponse
+ from backend.database import engine, Base
+ from backend.controllers import user_controller
+ import logging
+ import os
+ 
+ # Configure logging
+ logging.basicConfig(
+     level=logging.INFO,
+     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
+ )
+ logger = logging.getLogger(__name__)
+ 
+ app = FastAPI(
+     title="User Management API",
+     description="API for user information management with authentication",
+     version="1.0.0"
+ )
+ ... (更多)
```

### backend/database.py (新建, 707 chars)
```
+ from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
+ from sqlalchemy.orm import declarative_base
+ import os
+ 
+ DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")
+ 
+ engine = create_async_engine(
+     DATABASE_URL,
+     echo=False,
+     connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
+ )
+ 
+ AsyncSessionLocal = async_sessionmaker(
+     engine,
+     class_=AsyncSession,
+     expire_on_commit=False
+ )
+ 
+ Base = declarative_base()
+ 
+ ... (更多)
```

### tests/test_user_service.py (新建, 5464 chars)
```
+ import pytest
+ from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
+ from backend.models.user import User
+ from backend.services.user_service import UserService
+ from backend.schemas.user import UpdateUserInfoRequest
+ from backend.database import Base
+ from fastapi import HTTPException
+ import bcrypt
+ 
+ # Test database setup
+ TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
+ 
+ @pytest.fixture
+ async def db_session():
+     """Create test database session"""
+     engine = create_async_engine(TEST_DATABASE_URL, echo=False)
+     async with engine.begin() as conn:
+         await conn.run_sync(Base.metadata.create_all)
+     
+     AsyncTestSession = async_sessionmaker(
+ ... (更多)
```
