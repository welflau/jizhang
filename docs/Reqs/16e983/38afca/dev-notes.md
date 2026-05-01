# 开发笔记 — 用户注册与登录系统

> 2026-05-02 01:01 | LLM

## 产出文件
- [backend/app/models/user.py](/app#repo?file=backend/app/models/user.py) (1954 chars)
- [backend/app/utils/password.py](/app#repo?file=backend/app/utils/password.py) (794 chars)
- [backend/app/utils/jwt_handler.py](/app#repo?file=backend/app/utils/jwt_handler.py) (1412 chars)
- [backend/app/database.py](/app#repo?file=backend/app/database.py) (1253 chars)
- [backend/app/routers/auth.py](/app#repo?file=backend/app/routers/auth.py) (4510 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (1125 chars)
- [backend/requirements.txt](/app#repo?file=backend/requirements.txt) (162 chars)
- [backend/tests/test_auth_register.py](/app#repo?file=backend/tests/test_auth_register.py) (4050 chars)
- [backend/tests/test_auth_login.py](/app#repo?file=backend/tests/test_auth_login.py) (2425 chars)
- [frontend/index.html](/app#repo?file=frontend/index.html) (15806 chars)
- [backend/.env.example](/app#repo?file=backend/.env.example) (173 chars)
- [backend/.gitignore](/app#repo?file=backend/.gitignore) (253 chars)
- [README.md](/app#repo?file=README.md) (4372 chars)

## 自测: 自测 6/6 通过 ✅

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 13 个文件 |
| 入口文件 | ✅ | 存在 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 13 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/models/user.py (新建, 1954 chars)
```
+ from datetime import datetime
+ from typing import Optional
+ from pydantic import BaseModel, EmailStr, Field, field_validator
+ import re
+ 
+ 
+ class UserBase(BaseModel):
+     """Base user schema with common fields."""
+     email: Optional[EmailStr] = None
+     phone: Optional[str] = Field(None, min_length=11, max_length=11)
+ 
+     @field_validator('phone')
+     @classmethod
+     def validate_phone(cls, v: Optional[str]) -> Optional[str]:
+         if v is None:
+             return v
+         if not re.match(r'^1[3-9]\d{9}$', v):
+             raise ValueError('invalid phone number format')
+         return v
+ 
+ ... (更多)
```

### backend/app/utils/password.py (新建, 794 chars)
```
+ import bcrypt
+ 
+ 
+ def hash_password(password: str) -> str:
+     """Hash a plain password using bcrypt.
+     
+     Args:
+         password: Plain text password
+         
+     Returns:
+         Hashed password as string
+     """
+     salt = bcrypt.gensalt(rounds=12)
+     hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
+     return hashed.decode('utf-8')
+ 
+ 
+ def verify_password(plain_password: str, hashed_password: str) -> bool:
+     """Verify a plain password against hashed password.
+     
+ ... (更多)
```

### backend/app/utils/jwt_handler.py (新建, 1412 chars)
```
+ from datetime import datetime, timedelta
+ from typing import Optional
+ import os
+ import jwt
+ from jwt.exceptions import InvalidTokenError
+ 
+ 
+ SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
+ ALGORITHM = "HS256"
+ ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours default
+ 
+ 
+ def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
+     """Create JWT access token.
+     
+     Args:
+         data: Payload data to encode (must include 'sub' for user identifier)
+         expires_delta: Optional custom expiration time
+         
+     Returns:
+ ... (更多)
```

### backend/app/database.py (新建, 1253 chars)
```
+ import aiosqlite
+ import os
+ from contextlib import asynccontextmanager
+ 
+ 
+ DATABASE_PATH = os.getenv("DATABASE_PATH", "app.db")
+ 
+ 
+ async def init_db():
+     """Initialize database schema."""
+     async with aiosqlite.connect(DATABASE_PATH) as db:
+         await db.execute("""
+             CREATE TABLE IF NOT EXISTS users (
+                 id INTEGER PRIMARY KEY AUTOINCREMENT,
+                 email TEXT UNIQUE,
+                 phone TEXT UNIQUE,
+                 hashed_password TEXT NOT NULL,
+                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+                 is_active BOOLEAN DEFAULT 1,
+                 CONSTRAINT email_or_phone CHECK (email IS NOT NULL OR phone IS NOT NULL)
+ ... (更多)
```

### backend/app/routers/auth.py (新建, 4510 chars)
```
+ from fastapi import APIRouter, HTTPException, Depends, status
+ from datetime import timedelta
+ import aiosqlite
+ from typing import Optional
+ 
+ from ..models.user import UserCreate, UserResponse, LoginRequest, TokenResponse
+ from ..utils.password import hash_password, verify_password
+ from ..utils.jwt_handler import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
+ from ..database import get_db
+ 
+ 
+ router = APIRouter(prefix="/api/auth", tags=["authentication"])
+ 
+ 
+ @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
+ async def register_user(
+     user_data: UserCreate,
+     db: aiosqlite.Connection = Depends(get_db)
+ ):
+     """Register a new user with email/phone and password.
+ ... (更多)
```

### backend/app/main.py (新建, 1125 chars)
```
+ from fastapi import FastAPI
+ from fastapi.middleware.cors import CORSMiddleware
+ from contextlib import asynccontextmanager
+ import os
+ 
+ from .database import init_db
+ from .routers import auth
+ 
+ 
+ @asynccontextmanager
+ async def lifespan(app: FastAPI):
+     """Application lifespan manager."""
+     # Startup: initialize database
+     await init_db()
+     yield
+     # Shutdown: cleanup if needed
+ 
+ 
+ app = FastAPI(
+     title="User Authentication API",
+ ... (更多)
```

### backend/tests/test_auth_register.py (新建, 4050 chars)
```
+ import pytest
+ import sys
+ from pathlib import Path
+ 
+ # Add parent directory to path for imports
+ sys.path.insert(0, str(Path(__file__).parent.parent))
+ 
+ from fastapi.testclient import TestClient
+ from app.main import app
+ from app.database import init_db, DATABASE_PATH
+ import os
+ import aiosqlite
+ 
+ 
+ @pytest.fixture(scope="function")
+ async def test_db():
+     """Create a test database for each test."""
+     test_db_path = "test_app.db"
+     os.environ["DATABASE_PATH"] = test_db_path
+     
+ ... (更多)
```

### backend/tests/test_auth_login.py (新建, 2425 chars)
```
+ import pytest
+ import sys
+ from pathlib import Path
+ 
+ sys.path.insert(0, str(Path(__file__).parent.parent))
+ 
+ from fastapi.testclient import TestClient
+ from app.main import app
+ from app.database import init_db
+ import os
+ 
+ 
+ @pytest.fixture(scope="function")
+ async def test_db():
+     """Create a test database for each test."""
+     test_db_path = "test_login.db"
+     os.environ["DATABASE_PATH"] = test_db_path
+     
+     await init_db()
+     
+ ... (更多)
```

### frontend/index.html (新建, 15806 chars)
```
+ <!DOCTYPE html>
+ <html lang="en">
+ <head>
+     <meta charset="UTF-8">
+     <meta name="viewport" content="width=device-width, initial-scale=1.0">
+     <title>User Authentication</title>
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
+             --success: #1e8e3e;
+             --border: #dadce0;
+             --bg-gray: #f8f9fa;
+ ... (更多)
```

### backend/.env.example (新建, 173 chars)
```
+ # JWT Configuration
+ JWT_SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32
+ JWT_EXPIRE_MINUTES=1440
+ 
+ # Database
+ DATABASE_PATH=app.db
+ 
+ # Server
+ PORT=8080
+ 
```

### backend/.gitignore (新建, 253 chars)
```
+ # Python
+ __pycache__/
+ *.py[cod]
+ *$py.class
+ *.so
+ .Python
+ env/
+ venv/
+ ENV/
+ 
+ # Database
+ *.db
+ *.sqlite
+ *.sqlite3
+ 
+ # Environment variables
+ .env
+ .env.*
+ !.env.example
+ 
+ ... (更多)
```
