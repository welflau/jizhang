# 开发笔记 — Backend: Implement data export/import/clear APIs

> 2026-05-02 01:08 | LLM

## 产出文件
- [backend/app/models/__init__.py](/app#repo?file=backend/app/models/__init__.py) (59 chars)
- [backend/app/models/access_log.py](/app#repo?file=backend/app/models/access_log.py) (1094 chars)
- [backend/app/database.py](/app#repo?file=backend/app/database.py) (1114 chars)
- [backend/app/api/routes/export.py](/app#repo?file=backend/app/api/routes/export.py) (1504 chars)
- [backend/app/api/routes/import_data.py](/app#repo?file=backend/app/api/routes/import_data.py) (4247 chars)
- [backend/app/api/routes/clear.py](/app#repo?file=backend/app/api/routes/clear.py) (2294 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (2038 chars)
- [backend/requirements.txt](/app#repo?file=backend/requirements.txt) (101 chars)
- [backend/tests/test_export_import_clear.py](/app#repo?file=backend/tests/test_export_import_clear.py) (4950 chars)
- [backend/.env.example](/app#repo?file=backend/.env.example) (201 chars)
- [backend/README.md](/app#repo?file=backend/README.md) (2628 chars)

## 自测: 自测 6/6 通过 ✅

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 11 个文件 |
| 入口文件 | ✅ | 存在 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 11 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/models/__init__.py (新建, 59 chars)
```
+ from .access_log import AccessLog
+ 
+ __all__ = ["AccessLog"]
+ 
```

### backend/app/models/access_log.py (新建, 1094 chars)
```
+ from sqlalchemy import Column, Integer, String, DateTime, Index
+ from sqlalchemy.ext.declarative import declarative_base
+ from datetime import datetime
+ 
+ Base = declarative_base()
+ 
+ class AccessLog(Base):
+     """Access log record model
+     
+     Stores visitor access information including timestamp, IP, user agent and path.
+     """
+     __tablename__ = "access_logs"
+     
+     id = Column(Integer, primary_key=True, autoincrement=True)
+     timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
+     ip = Column(String(45), nullable=False)  # IPv6 max length
+     user_agent = Column(String(255), nullable=True)
+     path = Column(String(255), nullable=True)
+     
+     __table_args__ = (
+ ... (更多)
```

### backend/app/database.py (新建, 1114 chars)
```
+ import os
+ import aiosqlite
+ from contextlib import asynccontextmanager
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
+ DB_PATH = os.getenv("DB_PATH", "./data/app.db")
+ 
+ # Ensure data directory exists
+ os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
+ 
+ async def init_db():
+     """Initialize database schema"""
+     async with aiosqlite.connect(DB_PATH) as db:
+         await db.execute("""
+             CREATE TABLE IF NOT EXISTS access_logs (
+                 id INTEGER PRIMARY KEY AUTOINCREMENT,
+                 timestamp TEXT NOT NULL,
+                 ip TEXT NOT NULL,
+ ... (更多)
```

### backend/app/api/routes/export.py (新建, 1504 chars)
```
+ from fastapi import APIRouter, HTTPException
+ from fastapi.responses import JSONResponse
+ import logging
+ from app.database import get_db
+ 
+ logger = logging.getLogger(__name__)
+ router = APIRouter()
+ 
+ @router.get("/api/export")
+ async def export_records():
+     """Export all access records as JSON
+     
+     Returns:
+         JSON array of access log records sorted by timestamp descending
+     
+     Raises:
+         HTTPException: 500 if database query fails
+     """
+     try:
+         async with get_db() as db:
+ ... (更多)
```

### backend/app/api/routes/import_data.py (新建, 4247 chars)
```
+ from fastapi import APIRouter, HTTPException, UploadFile, File
+ from pydantic import BaseModel, Field, ValidationError
+ from typing import List
+ import json
+ import logging
+ from datetime import datetime
+ from app.database import get_db
+ 
+ logger = logging.getLogger(__name__)
+ router = APIRouter()
+ 
+ class AccessLogRecord(BaseModel):
+     """Schema for validating imported access log records"""
+     id: int = Field(gt=0)
+     timestamp: str
+     ip: str = Field(min_length=7, max_length=45)
+     user_agent: str | None = None
+     path: str | None = None
+ 
+ class ImportResponse(BaseModel):
+ ... (更多)
```

### backend/app/api/routes/clear.py (新建, 2294 chars)
```
+ from fastapi import APIRouter, HTTPException, Header
+ from pydantic import BaseModel
+ import os
+ import logging
+ from app.database import get_db
+ 
+ logger = logging.getLogger(__name__)
+ router = APIRouter()
+ 
+ class ClearResponse(BaseModel):
+     """Response schema for clear operation"""
+     success: bool
+     deleted: int
+ 
+ # Load admin token from environment
+ ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
+ 
+ if not ADMIN_TOKEN:
+     logger.warning("ADMIN_TOKEN not set, clear endpoint will reject all requests")
+ 
+ ... (更多)
```

### backend/app/main.py (新建, 2038 chars)
```
+ from fastapi import FastAPI, Request, HTTPException
+ from fastapi.responses import JSONResponse
+ from fastapi.middleware.cors import CORSMiddleware
+ import logging
+ import os
+ from contextlib import asynccontextmanager
+ 
+ from app.database import init_db
+ from app.api.routes import export, import_data, clear
+ 
+ # Configure logging
+ logging.basicConfig(
+     level=logging.INFO,
+     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
+ )
+ logger = logging.getLogger(__name__)
+ 
+ @asynccontextmanager
+ async def lifespan(app: FastAPI):
+     """Application lifespan manager"""
+ ... (更多)
```

### backend/tests/test_export_import_clear.py (新建, 4950 chars)
```
+ import pytest
+ import json
+ import os
+ from fastapi.testclient import TestClient
+ from app.main import app
+ from app.database import get_db, init_db, DB_PATH
+ import aiosqlite
+ from datetime import datetime
+ 
+ # Use test database
+ test_db_path = "./data/test_app.db"
+ os.environ["DB_PATH"] = test_db_path
+ os.environ["ADMIN_TOKEN"] = "test_admin_token_12345"
+ 
+ client = TestClient(app)
+ 
+ @pytest.fixture(autouse=True)
+ async def setup_teardown():
+     """Setup test database before each test and cleanup after"""
+     # Remove existing test db
+ ... (更多)
```

### backend/.env.example (新建, 201 chars)
```
+ # Database configuration
+ DB_PATH=./data/app.db
+ 
+ # Admin token for clear endpoint (MUST be set in production)
+ ADMIN_TOKEN=your_secure_random_token_here
+ 
+ # Server configuration
+ PORT=8080
+ ENV=development
+ 
```
