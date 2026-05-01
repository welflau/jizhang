# 开发笔记 — 用户信息更新 API 开发

> 2026-05-02 01:08 | LLM

## 产出文件
- [backend/models/user.py](/app#repo?file=backend/models/user.py) (3602 chars)
- [backend/services/user_service.py](/app#repo?file=backend/services/user_service.py) (5327 chars)
- [backend/middleware/auth.py](/app#repo?file=backend/middleware/auth.py) (2467 chars)
- [backend/routes/user_routes.py](/app#repo?file=backend/routes/user_routes.py) (3022 chars)
- [backend/main.py](/app#repo?file=backend/main.py) (1617 chars)
- [backend/tests/test_user_routes.py](/app#repo?file=backend/tests/test_user_routes.py) (8425 chars)
- [backend/requirements.txt](/app#repo?file=backend/requirements.txt) (178 chars)
- [backend/init_db.py](/app#repo?file=backend/init_db.py) (1466 chars)
- [README.md](/app#repo?file=README.md) (6020 chars)

## 自测: 自测 6/6 通过 ✅

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 9 个文件 |
| 入口文件 | ✅ | 存在 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 9 个文件已落盘 |

## 代码变更 (Diff)

### backend/models/user.py (新建, 3602 chars)
```
+ from datetime import datetime
+ from typing import Optional
+ from pydantic import BaseModel, Field, validator
+ import re
+ 
+ class UserPreferences(BaseModel):
+     """User preference settings"""
+     theme: str = Field(default="light", description="UI theme: light/dark")
+     language: str = Field(default="en", description="Interface language")
+     notifications_enabled: bool = Field(default=True, description="Enable notifications")
+     email_notifications: bool = Field(default=True, description="Enable email notifications")
+ 
+     class Config:
+         json_schema_extra = {
+             "example": {
+                 "theme": "dark",
+                 "language": "zh",
+                 "notifications_enabled": True,
+                 "email_notifications": False
+             }
+ ... (更多)
```

### backend/services/user_service.py (新建, 5327 chars)
```
+ import aiosqlite
+ import bcrypt
+ import json
+ from datetime import datetime
+ from typing import Optional, Dict, Any
+ from fastapi import HTTPException
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
+ class UserService:
+     """User service for database operations"""
+     
+     def __init__(self, db_path: str = "app.db"):
+         self.db_path = db_path
+     
+     async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
+         """Get user by ID
+         
+         Args:
+ ... (更多)
```

### backend/middleware/auth.py (新建, 2467 chars)
```
+ from fastapi import Request, HTTPException, status
+ from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
+ import jwt
+ import os
+ from typing import Optional
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
+ # JWT configuration
+ JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
+ JWT_ALGORITHM = "HS256"
+ 
+ security = HTTPBearer()
+ 
+ class AuthMiddleware:
+     """JWT authentication middleware"""
+     
+     @staticmethod
+     def decode_token(token: str) -> Optional[dict]:
+ ... (更多)
```

### backend/routes/user_routes.py (新建, 3022 chars)
```
+ from fastapi import APIRouter, Depends, HTTPException, status
+ from backend.models.user import UserUpdateRequest, UserResponse
+ from backend.services.user_service import UserService
+ from backend.middleware.auth import get_current_user
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
+ router = APIRouter(prefix="/api/user", tags=["user"])
+ user_service = UserService()
+ 
+ @router.get("/profile", response_model=UserResponse)
+ async def get_profile(current_user: dict = Depends(get_current_user)):
+     """Get current user profile
+     
+     Args:
+         current_user: Authenticated user from JWT token
+         
+     Returns:
+         User profile data
+ ... (更多)
```

### backend/main.py (新建, 1617 chars)
```
+ from fastapi import FastAPI, Request
+ from fastapi.responses import JSONResponse
+ from fastapi.middleware.cors import CORSMiddleware
+ from backend.routes import user_routes
+ import logging
+ import os
+ 
+ # Configure logging
+ logging.basicConfig(
+     level=logging.INFO,
+     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
+ )
+ logger = logging.getLogger(__name__)
+ 
+ app = FastAPI(
+     title="User Profile API",
+     description="API for user profile management with authentication",
+     version="1.0.0"
+ )
+ 
+ ... (更多)
```

### backend/tests/test_user_routes.py (新建, 8425 chars)
```
+ import pytest
+ from fastapi.testclient import TestClient
+ from backend.main import app
+ from backend.middleware.auth import AuthMiddleware
+ import aiosqlite
+ import bcrypt
+ import json
+ import os
+ 
+ client = TestClient(app)
+ 
+ # Test database path
+ TEST_DB = "test_app.db"
+ 
+ @pytest.fixture(scope="module")
+ async def setup_test_db():
+     """Setup test database with sample user"""
+     # Remove existing test db
+     if os.path.exists(TEST_DB):
+         os.remove(TEST_DB)
+ ... (更多)
```

### backend/init_db.py (新建, 1466 chars)
```
+ import asyncio
+ import aiosqlite
+ import os
+ 
+ DB_PATH = "app.db"
+ 
+ async def init_database():
+     """Initialize database schema"""
+     # Remove existing db for fresh start (only for development)
+     if os.path.exists(DB_PATH):
+         print(f"Removing existing database: {DB_PATH}")
+         os.remove(DB_PATH)
+     
+     async with aiosqlite.connect(DB_PATH) as db:
+         # Enable foreign keys
+         await db.execute("PRAGMA foreign_keys = ON")
+         
+         # Create users table
+         await db.execute("""
+             CREATE TABLE IF NOT EXISTS users (
+ ... (更多)
```
