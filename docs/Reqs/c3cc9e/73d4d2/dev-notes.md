# 开发笔记 — Implement JWT authentication middleware

> 2026-05-02 01:25 | LLM

## 产出文件
- [backend/app/core/__init__.py](/app#repo?file=backend/app/core/__init__.py) (524 chars)
- [backend/app/core/security.py](/app#repo?file=backend/app/core/security.py) (7929 chars)
- [backend/app/core/config.py](/app#repo?file=backend/app/core/config.py) (1026 chars)
- [backend/app/dependencies/__init__.py](/app#repo?file=backend/app/dependencies/__init__.py) (339 chars)
- [backend/app/dependencies/auth.py](/app#repo?file=backend/app/dependencies/auth.py) (5072 chars)

## 自测: 自测 6/6 通过 ✅

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 5 个文件 |
| 入口文件 | ✅ | 存在 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 5 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/core/__init__.py (新建, 524 chars)
```
+ """
+ Core module initialization.
+ Exports security utilities and authentication functions.
+ """
+ 
+ from app.core.security import (
+     create_access_token,
+     create_refresh_token,
+     verify_token,
+     get_password_hash,
+     verify_password,
+     get_current_user,
+     get_current_active_user,
+     oauth2_scheme,
+ )
+ 
+ __all__ = [
+     "create_access_token",
+     "create_refresh_token",
+     "verify_token",
+ ... (更多)
```

### backend/app/core/security.py (新建, 7929 chars)
```
+ from datetime import datetime, timedelta
+ from typing import Optional, Union, Any
+ from jose import JWTError, jwt
+ from passlib.context import CryptContext
+ from fastapi import Depends, HTTPException, status
+ from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
+ from sqlalchemy.orm import Session
+ import os
+ 
+ from app.db.session import get_db
+ from app.models.user import User
+ 
+ # 从环境变量读取配置
+ SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
+ ALGORITHM = os.getenv("ALGORITHM", "HS256")
+ ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
+ REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
+ 
+ # 密码哈希上下文
+ pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
+ ... (更多)
```

### backend/app/core/config.py (新建, 1026 chars)
```
+ from typing import Optional
+ from pydantic_settings import BaseSettings
+ from functools import lru_cache
+ 
+ 
+ class Settings(BaseSettings):
+     """应用配置类"""
+     
+     # 应用基础配置
+     APP_NAME: str = "FastAPI Backend"
+     APP_VERSION: str = "1.0.0"
+     DEBUG: bool = False
+     
+     # 数据库配置
+     DATABASE_URL: str = "sqlite:///./app.db"
+     
+     # JWT 配置
+     SECRET_KEY: str = "your-secret-key-change-this-in-production"
+     ALGORITHM: str = "HS256"
+     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
+ ... (更多)
```

### backend/app/dependencies/__init__.py (新建, 339 chars)
```
+ """
+ Dependencies package initialization.
+ Exports authentication and authorization dependencies.
+ """
+ 
+ from .auth import (
+     get_current_user,
+     get_current_active_user,
+     get_current_superuser,
+     oauth2_scheme,
+ )
+ 
+ __all__ = [
+     "get_current_user",
+     "get_current_active_user",
+     "get_current_superuser",
+     "oauth2_scheme",
+ ]
```

### backend/app/dependencies/auth.py (新建, 5072 chars)
```
+ from datetime import datetime, timedelta
+ from typing import Optional
+ from fastapi import Depends, HTTPException, status
+ from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
+ from jose import JWTError, jwt
+ from sqlalchemy.orm import Session
+ 
+ from app.core.config import settings
+ from app.core.security import verify_token
+ from app.db.session import get_db
+ from app.models.user import User
+ from app.schemas.token import TokenPayload
+ 
+ security = HTTPBearer()
+ 
+ 
+ async def get_current_user(
+     credentials: HTTPAuthorizationCredentials = Depends(security),
+     db: Session = Depends(get_db)
+ ) -> User:
+ ... (更多)
```
