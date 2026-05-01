# 开发笔记 — Create unified response format and exception handler middleware

> 2026-05-02 01:24 | LLM

## 产出文件
- [backend/app/schemas/response.py](/app#repo?file=backend/app/schemas/response.py) (3772 chars)
- [backend/app/core/exceptions.py](/app#repo?file=backend/app/core/exceptions.py) (4169 chars)
- [backend/app/middleware/__init__.py](/app#repo?file=backend/app/middleware/__init__.py) (2573 chars)
- [backend/app/middleware/exception_handler.py](/app#repo?file=backend/app/middleware/exception_handler.py) (4570 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (2048 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 5 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 5 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/schemas/response.py (新建, 3772 chars)
```
+ from typing import Any, Optional, Generic, TypeVar
+ from pydantic import BaseModel
+ from fastapi import status
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
+ ... (更多)
```

### backend/app/core/exceptions.py (新建, 4169 chars)
```
+ from typing import Any, Optional
+ 
+ 
+ class AppException(Exception):
+     """Base application exception"""
+     
+     def __init__(
+         self,
+         message: str = "An error occurred",
+         code: int = 500,
+         data: Optional[Any] = None
+     ):
+         self.message = message
+         self.code = code
+         self.data = data
+         super().__init__(self.message)
+ 
+ 
+ class NotFoundError(AppException):
+     """Resource not found exception"""
+ ... (更多)
```

### backend/app/middleware/__init__.py (新建, 2573 chars)
```
+ from fastapi import Request, status
+ from fastapi.responses import JSONResponse
+ from fastapi.exceptions import RequestValidationError
+ from starlette.exceptions import HTTPException as StarletteHTTPException
+ from app.schemas.response import ResponseModel
+ from app.core.exceptions import BusinessException
+ import logging
+ import traceback
+ 
+ logger = logging.getLogger(__name__)
+ 
+ 
+ async def exception_handler_middleware(request: Request, call_next):
+     """全局异常处理中间件"""
+     try:
+         response = await call_next(request)
+         return response
+     except BusinessException as e:
+         logger.warning(f"Business exception: {e.message}, code: {e.code}")
+         return JSONResponse(
+ ... (更多)
```

### backend/app/middleware/exception_handler.py (新建, 4570 chars)
```
+ from fastapi import Request, status
+ from fastapi.responses import JSONResponse
+ from fastapi.exceptions import RequestValidationError
+ from starlette.exceptions import HTTPException as StarletteHTTPException
+ from sqlalchemy.exc import SQLAlchemyError
+ import logging
+ import traceback
+ from typing import Union
+ 
+ logger = logging.getLogger(__name__)
+ 
+ 
+ class BaseAPIException(Exception):
+     """基础API异常类"""
+     def __init__(self, message: str = "Internal Server Error", code: int = 500):
+         self.message = message
+         self.code = code
+         super().__init__(self.message)
+ 
+ 
+ ... (更多)
```

### backend/app/main.py (修改)
```diff
--- a/backend/app/main.py
+++ b/backend/app/main.py
@@ -1,5 +1,6 @@
-from fastapi import FastAPI

+from fastapi import FastAPI, Request, status

 from fastapi.middleware.cors import CORSMiddleware

+from fastapi.responses import JSONResponse

 from backend.app.core.config import settings

 from backend.app.core.database import init_db

 from backend.app.routers import auth

@@ -26,6 +27,26 @@
     allow_headers=["*"],

 )

 

+

+# Exception handler middleware

+@app.middleware("http")

+async def exception_handler_middleware(request: Request, call_next):

+    """Unified exception handler middleware."""

+    try:

+        response = await call_next(request)

+        return response

+    except Exception as exc:

+        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

+        return JSONResponse(

+            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

+            content={

+                "success": False,

+                "message": "Internal server error",

+                "data": None

+            }

+        )

+

+

 # Include routers

 app.include_router(auth.router)

 

@@ -41,7 +62,14 @@
 @app.get("/")

 async def root():

     """Health check endpoint."""

-    return {"status": "ok", "app": settings.APP_NAME}

+    return {

+        "success": True,

+        "message": "OK",

+        "data": {

+            "status": "ok",

+            "app": settings.APP_NAME

+        }

+    }

... (共 53 行变更)
```
