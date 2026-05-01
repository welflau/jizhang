# 开发笔记 — Create unified response format and exception handler middleware

> 2026-05-02 01:31 | LLM

## 产出文件
- [app/schemas/response.py](/app#repo?file=app/schemas/response.py) (2935 chars)
- [app/core/exceptions.py](/app#repo?file=app/core/exceptions.py) (2729 chars)
- [app/middleware/exception_handler.py](/app#repo?file=app/middleware/exception_handler.py) (4353 chars)
- [app/middleware/__init__.py](/app#repo?file=app/middleware/__init__.py) (229 chars)
- [app/api/test.py](/app#repo?file=app/api/test.py) (3961 chars)
- [diagnosis.md](/app#repo?file=diagnosis.md) (2629 chars)
- [app/main.py](/app#repo?file=app/main.py) (3083 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (3346 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 8 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 8 个文件已落盘 |

## 代码变更 (Diff)

### app/schemas/response.py (新建, 2935 chars)
```
+ from typing import Generic, TypeVar, Optional, Any
+ from pydantic import BaseModel
+ 
+ T = TypeVar('T')
+ 
+ 
+ class ResponseModel(BaseModel, Generic[T]):
+     """统一响应模型"""
+     code: int = 200
+     message: str = "success"
+     data: Optional[T] = None
+ 
+     class Config:
+         json_schema_extra = {
+             "example": {
+                 "code": 200,
+                 "message": "success",
+                 "data": None
+             }
+         }
+ ... (更多)
```

### app/core/exceptions.py (新建, 2729 chars)
```
+ app/core/exceptions.py
+ 
+ from typing import Any, Optional
+ 
+ 
+ class AppException(Exception):
+     """Base application exception"""
+     
+     def __init__(
+         self,
+         message: str = "Application error",
+         code: int = 500,
+         data: Optional[Any] = None
+     ):
+         self.message = message
+         self.code = code
+         self.data = data
+         super().__init__(self.message)
+ 
+ 
+ ... (更多)
```

### app/middleware/exception_handler.py (新建, 4353 chars)
```
+ import logging
+ from typing import Union
+ from fastapi import Request, status
+ from fastapi.responses import JSONResponse
+ from fastapi.exceptions import RequestValidationError
+ from starlette.exceptions import HTTPException as StarletteHTTPException
+ from app.core.exceptions import (
+     BaseAPIException,
+     NotFoundError,
+     ValidationError,
+     UnauthorizedError,
+     ForbiddenError,
+     InternalServerError
+ )
+ from app.schemas.response import ResponseModel
+ 
+ logger = logging.getLogger(__name__)
+ 
+ 
+ async def exception_handler_middleware(request: Request, call_next):
+ ... (更多)
```

### app/middleware/__init__.py (新建, 229 chars)
```
+ from app.middleware.exception_handler import ExceptionHandlerMiddleware
+ from app.middleware.response_formatter import ResponseFormatterMiddleware
+ 
+ __all__ = [
+     "ExceptionHandlerMiddleware",
+     "ResponseFormatterMiddleware",
+ ]
```

### app/api/test.py (新建, 3961 chars)
```
+ import pytest
+ from fastapi.testclient import TestClient
+ from app.main import app
+ from app.core.exceptions import NotFoundError, ValidationError, BusinessError
+ 
+ client = TestClient(app)
+ 
+ 
+ def test_success_response():
+     """测试成功响应格式"""
+     response = client.get("/api/v1/health")
+     assert response.status_code == 200
+     data = response.json()
+     assert "code" in data
+     assert "message" in data
+     assert "data" in data
+     assert data["code"] == 200
+     assert data["message"] == "success"
+ 
+ 
+ ... (更多)
```

### app/main.py (修改)
```diff
--- a/app/main.py
+++ b/app/main.py
@@ -2,8 +2,11 @@
 import os

 import logging

 from contextlib import asynccontextmanager

-from fastapi import FastAPI

+from fastapi import FastAPI, Request, status

 from fastapi.middleware.cors import CORSMiddleware

+from fastapi.responses import JSONResponse

+from fastapi.exceptions import RequestValidationError

+from starlette.exceptions import HTTPException as StarletteHTTPException

 from app.core.config import settings

 from app.core.logger import setup_logging

 from app.api import health

@@ -41,6 +44,60 @@
     allow_headers=["*"],

 )

 

+

+# Exception handlers

+@app.exception_handler(StarletteHTTPException)

+async def http_exception_handler(request: Request, exc: StarletteHTTPException):

+    """Handle HTTP exceptions with unified response format."""

+    return JSONResponse(

+        status_code=exc.status_code,

+        content={

+            "success": False,

+            "data": None,

+            "error": {

+                "code": exc.status_code,

+                "message": exc.detail

+            }

+        }

+    )

+

+

+@app.exception_handler(RequestValidationError)

+async def validation_exception_handler(request: Request, exc: RequestValidationError):

+    """Handle validation errors with unified response format."""

+    return JSONResponse(

+        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,

+        content={

+            "success": False,

+            "data": None,

+            "error": {

+                "code": 422,

+                "message": "Validation error",

+                "details": exc.errors()

+            }

... (共 82 行变更)
```

### backend/app/main.py (修改)
```diff
--- a/backend/app/main.py
+++ b/backend/app/main.py
@@ -1,5 +1,8 @@
-from fastapi import FastAPI

+from fastapi import FastAPI, Request, status

 from fastapi.middleware.cors import CORSMiddleware

+from fastapi.responses import JSONResponse

+from fastapi.exceptions import RequestValidationError

+from starlette.exceptions import HTTPException as StarletteHTTPException

 from backend.app.core.config import settings

 from backend.app.core.database import init_db

 from backend.app.routers import auth

@@ -25,6 +28,64 @@
     allow_methods=["*"],

     allow_headers=["*"],

 )

+

+

+# Unified response format helper

+def unified_response(success: bool, data=None, message: str = "", code: int = 200):

+    """Create unified response format."""

+    return {

+        "success": success,

+        "data": data,

+        "message": message,

+        "code": code

+    }

+

+

+# Global exception handlers

+@app.exception_handler(StarletteHTTPException)

+async def http_exception_handler(request: Request, exc: StarletteHTTPException):

+    """Handle HTTP exceptions with unified format."""

+    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")

+    return JSONResponse(

+        status_code=exc.status_code,

+        content=unified_response(

+            success=False,

+            data=None,

+            message=str(exc.detail),

+            code=exc.status_code

+        )

+    )

+

+

+@app.exception_handler(RequestValidationError)

+async def validation_exception_handler(request: Request, exc: RequestValidationError):

+    """Handle validation errors with unified format."""

+    logger.error(f"Validation error: {exc.errors()}")

+    return JSONResponse(

... (共 77 行变更)
```
