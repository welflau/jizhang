# 开发笔记 — 用户注册与登录系统

> 2026-05-02 01:16 | LLM

## 产出文件
- [backend/hello_world.py](/app#repo?file=backend/hello_world.py) (10251 chars)
- [backend/auth/__init__.py](/app#repo?file=backend/auth/__init__.py) (374 chars)
- [backend/auth/models.py](/app#repo?file=backend/auth/models.py) (6030 chars)
- [backend/auth/schemas.py](/app#repo?file=backend/auth/schemas.py) (8172 chars)
- [backend/auth/security.py](/app#repo?file=backend/auth/security.py) (6663 chars)
- [backend/auth/routes.py](/app#repo?file=backend/auth/routes.py) (11492 chars)
- [backend/database/migrations/20240102_000001_create_users.sql](/app#repo?file=backend/database/migrations/20240102_000001_create_users.sql) (4742 chars)
- [tests/__init__.py](/app#repo?file=tests/__init__.py) (1271 chars)
- [tests/test_hello_world.py](/app#repo?file=tests/test_hello_world.py) (13185 chars)
- [tests/test_register.py](/app#repo?file=tests/test_register.py) (20699 chars)
- [frontend/index.html](/app#repo?file=frontend/index.html) (24665 chars)
- [.env.example](/app#repo?file=.env.example) (1863 chars)
- [backend/main.py](/app#repo?file=backend/main.py) (2354 chars)

## 自测: 自测 4/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 13 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ❌ | backend/auth/routes.py: invalid syntax (line 203) |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 13 个文件已落盘 |

## 代码变更 (Diff)

### backend/hello_world.py (新建, 10251 chars)
```
+ from fastapi import FastAPI, HTTPException, Depends, status
+ from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
+ from fastapi.middleware.cors import CORSMiddleware
+ from pydantic import BaseModel, EmailStr, Field
+ from typing import Optional
+ import bcrypt
+ import jwt
+ from datetime import datetime, timedelta
+ import os
+ from dotenv import load_dotenv
+ import re
+ 
+ load_dotenv()
+ 
+ app = FastAPI(title="User Authentication System")
+ 
+ # CORS配置
+ app.add_middleware(
+     CORSMiddleware,
+     allow_origins=["*"],
+ ... (更多)
```

### backend/auth/__init__.py (新建, 374 chars)
```
+ from .jwt_handler import create_access_token, verify_token, decode_token
+ from .password import hash_password, verify_password
+ from .dependencies import get_current_user, get_current_active_user
+ 
+ __all__ = [
+     "create_access_token",
+     "verify_token",
+     "decode_token",
+     "hash_password",
+     "verify_password",
+     "get_current_user",
+     "get_current_active_user",
+ ]
```

### backend/auth/models.py (新建, 6030 chars)
```
+ from datetime import datetime
+ from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
+ from sqlalchemy.orm import relationship
+ from backend.database import Base
+ import enum
+ 
+ 
+ class UserStatus(str, enum.Enum):
+     """用户状态枚举"""
+     ACTIVE = "active"
+     INACTIVE = "inactive"
+     SUSPENDED = "suspended"
+     DELETED = "deleted"
+ 
+ 
+ class LoginMethod(str, enum.Enum):
+     """登录方式枚举"""
+     EMAIL = "email"
+     PHONE = "phone"
+ 
+ ... (更多)
```

### backend/auth/schemas.py (新建, 8172 chars)
```
+ from pydantic import BaseModel, EmailStr, Field, validator
+ from typing import Optional
+ from datetime import datetime
+ import re
+ 
+ 
+ class UserRegisterSchema(BaseModel):
+     """用户注册模式"""
+     email: Optional[EmailStr] = None
+     phone: Optional[str] = None
+     password: str = Field(..., min_length=8, max_length=128)
+     confirm_password: str
+     username: str = Field(..., min_length=3, max_length=50)
+ 
+     @validator('phone')
+     def validate_phone(cls, v):
+         if v:
+             # 验证手机号格式（中国大陆）
+             pattern = r'^1[3-9]\d{9}$'
+             if not re.match(pattern, v):
+ ... (更多)
```

### backend/auth/security.py (新建, 6663 chars)
```
+ import os
+ from datetime import datetime, timedelta
+ from typing import Optional, Union
+ from jose import JWTError, jwt
+ from passlib.context import CryptContext
+ from fastapi import HTTPException, status
+ from dotenv import load_dotenv
+ 
+ load_dotenv()
+ 
+ # 密码加密上下文
+ pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
+ 
+ # JWT 配置
+ SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
+ ALGORITHM = os.getenv("ALGORITHM", "HS256")
+ ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
+ REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
+ 
+ 
+ ... (更多)
```

### backend/auth/routes.py (新建, 11492 chars)
```
+ from datetime import datetime, timedelta
+ from typing import Optional
+ from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
+ from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
+ from sqlalchemy.orm import Session
+ from jose import JWTError, jwt
+ from passlib.context import CryptContext
+ import secrets
+ import re
+ 
+ from backend.database import get_db
+ from backend.models import User, PasswordResetToken
+ from backend.schemas import (
+     UserCreate,
+     UserLogin,
+     UserResponse,
+     Token,
+     PasswordResetRequest,
+     PasswordReset,
+     MessageResponse
+ ... (更多)
```

### backend/database/migrations/20240102_000001_create_users.sql (新建, 4742 chars)
```
+ -- 创建用户表
+ CREATE TABLE IF NOT EXISTS users (
+     id SERIAL PRIMARY KEY,
+     username VARCHAR(50) UNIQUE NOT NULL,
+     email VARCHAR(255) UNIQUE NOT NULL,
+     phone VARCHAR(20) UNIQUE,
+     password_hash VARCHAR(255) NOT NULL,
+     is_active BOOLEAN DEFAULT TRUE,
+     is_verified BOOLEAN DEFAULT FALSE,
+     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
+     updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
+     last_login_at TIMESTAMP WITH TIME ZONE,
+     CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
+     CONSTRAINT phone_format CHECK (phone IS NULL OR phone ~* '^\+?[1-9]\d{1,14}$')
+ );
+ 
+ -- 创建密码重置令牌表
+ CREATE TABLE IF NOT EXISTS password_reset_tokens (
+     id SERIAL PRIMARY KEY,
+     user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
+ ... (更多)
```

### tests/__init__.py (新建, 1271 chars)
```
+ """
+ Tests package initialization.
+ This module initializes the test suite for the user authentication system.
+ """
+ 
+ import os
+ import sys
+ from pathlib import Path
+ 
+ # Add the project root directory to Python path
+ project_root = Path(__file__).parent.parent
+ sys.path.insert(0, str(project_root))
+ 
+ # Test configuration
+ TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
+ TEST_SECRET_KEY = os.getenv("TEST_SECRET_KEY", "test-secret-key-for-testing-only")
+ TEST_ALGORITHM = "HS256"
+ TEST_ACCESS_TOKEN_EXPIRE_MINUTES = 30
+ 
+ # Test user data
+ ... (更多)
```

### tests/test_hello_world.py (新建, 13185 chars)
```
+ import pytest
+ from fastapi.testclient import TestClient
+ from datetime import datetime, timedelta
+ import jwt
+ from app.main import app
+ from app.core.security import get_password_hash, verify_password, create_access_token
+ from app.core.config import settings
+ 
+ client = TestClient(app)
+ 
+ 
+ class TestUserRegistration:
+     """测试用户注册功能"""
+ 
+     def test_register_with_email_success(self):
+         """测试邮箱注册成功"""
+         response = client.post(
+             "/api/auth/register",
+             json={
+                 "email": "test@example.com",
+ ... (更多)
```

### tests/test_register.py (新建, 20699 chars)
```
+ import pytest
+ from fastapi.testclient import TestClient
+ from datetime import datetime, timedelta
+ from jose import jwt
+ import re
+ 
+ from app.main import app
+ from app.core.config import settings
+ from app.core.security import verify_password, get_password_hash
+ from app.models.user import User
+ from app.db.session import get_db
+ 
+ client = TestClient(app)
+ 
+ 
+ class TestUserRegistration:
+     """用户注册测试"""
+ 
+     def test_register_with_email_success(self, db_session):
+         """测试邮箱注册成功"""
+ ... (更多)
```

### frontend/index.html (新建, 24665 chars)
```
+ <!DOCTYPE html>
+ <html lang="zh-CN">
+ <head>
+     <meta charset="UTF-8">
+     <meta name="viewport" content="width=device-width, initial-scale=1.0">
+     <title>用户认证系统</title>
+     <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
+     <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
+     <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
+     <style>
+         * {
+             margin: 0;
+             padding: 0;
+             box-sizing: border-box;
+         }
+ 
+         body {
+             font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
+             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
+             min-height: 100vh;
+ ... (更多)
```

### .env.example (新建, 1863 chars)
```
+ # Application Configuration
+ APP_NAME=User Authentication System
+ APP_ENV=development
+ DEBUG=True
+ 
+ # Server Configuration
+ HOST=0.0.0.0
+ PORT=8000
+ 
+ # Database Configuration
+ DATABASE_URL=postgresql://username:password@localhost:5432/auth_db
+ DATABASE_ECHO=False
+ 
+ # Redis Configuration (for session/cache)
+ REDIS_URL=redis://localhost:6379/0
+ 
+ # JWT Configuration
+ JWT_SECRET_KEY=your-secret-key-change-this-in-production
+ JWT_ALGORITHM=HS256
+ JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
+ ... (更多)
```

### backend/main.py (修改)
```diff
--- a/backend/main.py
+++ b/backend/main.py
@@ -10,6 +10,7 @@
 from contextlib import asynccontextmanager

 

 from database import init_database

+from routes import auth

 

 # Configure logging

 logging.basicConfig(

@@ -53,6 +54,9 @@
     allow_headers=["*"],

 )

 

+# Register routers

+app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

+

 

 @app.get("/")

 async def root():

@@ -90,4 +94,4 @@
         host="0.0.0.0",

         port=port,

         reload=os.getenv("ENV") == "development"

-    )

+    )
```
