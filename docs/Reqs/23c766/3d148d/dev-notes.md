# 开发笔记 — Frontend: Add data backup and restore UI

> 2026-05-02 01:22 | LLM

## 产出文件
- [backend/main.py](/app#repo?file=backend/main.py) (16140 chars)

## 自测: 自测 6/6 通过 ✅

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 1 个文件 |
| 入口文件 | ✅ | 存在 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 1 个文件已落盘 |

## 代码变更 (Diff)

### backend/main.py (修改)
```diff
--- a/backend/main.py
+++ b/backend/main.py
@@ -1,5 +1,7 @@
 import os

 import logging

+import json

+import shutil

 from datetime import datetime, timedelta

 from typing import Optional

 

@@ -7,6 +9,7 @@
 from fastapi import FastAPI, HTTPException, Depends, status

 from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

 from fastapi.middleware.cors import CORSMiddleware

+from fastapi.responses import FileResponse

 from pydantic import BaseModel, Field, EmailStr

 import aiosqlite

 import bcrypt

@@ -21,6 +24,7 @@
 JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

 DB_PATH = os.getenv("DB_PATH", "app.db")

 PORT = int(os.getenv("PORT", "8080"))

+BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")

 

 app = FastAPI(title="User Auth API")

 

@@ -73,6 +77,16 @@
 

 class MessageResponse(BaseModel):

     message: str

+

+

+class BackupResponse(BaseModel):

+    filename: str

+    created_at: str

+    size: int

+

+

+class RestoreRequest(BaseModel):

+    filename: str

 

 

 # Database dependency

@@ -112,6 +126,8 @@
 @app.on_event("startup")

 async def startup_event():

     await init_db()

+    # Create backup directory if it doesn't exist

+    os.makedirs(BACKUP_DIR, exist_ok=True)

 

... (共 200 行变更)
```
