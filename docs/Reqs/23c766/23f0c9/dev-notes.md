# 开发笔记 — Backend: Implement data export/import/clear APIs

> 2026-05-02 01:07 | LLM

## 产出文件
- [backend/app/routers/data_management.py](/app#repo?file=backend/app/routers/data_management.py) (8147 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (2378 chars)
- [backend/tests/test_data_management.py](/app#repo?file=backend/tests/test_data_management.py) (7893 chars)
- [backend/requirements.txt](/app#repo?file=backend/requirements.txt) (196 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 4 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 4 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/routers/data_management.py (新建, 8147 chars)
```
+ from fastapi import APIRouter, HTTPException, UploadFile, File, Header, Depends
+ from fastapi.responses import JSONResponse
+ from sqlalchemy.orm import Session
+ from sqlalchemy import text
+ import json
+ import logging
+ from typing import Optional
+ from datetime import datetime
+ 
+ from ..database import get_db
+ from ..models import AccessLog
+ 
+ logger = logging.getLogger(__name__)
+ router = APIRouter()
+ 
+ 
+ @router.get("/export")
+ async def export_data(db: Session = Depends(get_db)):
+     """
+     Export all access records as JSON, sorted by timestamp descending.
+ ... (更多)
```

### backend/app/main.py (新建, 2378 chars)
```
+ from fastapi import FastAPI, Request
+ from fastapi.middleware.cors import CORSMiddleware
+ from fastapi.staticfiles import StaticFiles
+ from fastapi.responses import FileResponse
+ import logging
+ from pathlib import Path
+ 
+ from .database import engine, Base
+ from .routers import data_management
+ from .models import AccessLog
+ 
+ # Configure logging
+ logging.basicConfig(
+     level=logging.INFO,
+     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
+ )
+ logger = logging.getLogger(__name__)
+ 
+ # Create database tables
+ Base.metadata.create_all(bind=engine)
+ ... (更多)
```

### backend/tests/test_data_management.py (新建, 7893 chars)
```
+ import pytest
+ import json
+ from fastapi.testclient import TestClient
+ from datetime import datetime
+ from io import BytesIO
+ 
+ from app.main import app
+ from app.database import Base, engine, SessionLocal
+ from app.models import AccessLog
+ 
+ # Create test client
+ client = TestClient(app)
+ 
+ 
+ @pytest.fixture(autouse=True)
+ def setup_database():
+     """Create tables before each test and clean up after"""
+     Base.metadata.create_all(bind=engine)
+     yield
+     Base.metadata.drop_all(bind=engine)
+ ... (更多)
```
