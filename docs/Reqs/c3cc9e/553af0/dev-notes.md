# 开发笔记 — Create unified response format and exception handler middleware

> 2026-05-02 01:31 | LLM

## 产出文件
- [backend/app/schemas/response.py](/app#repo?file=backend/app/schemas/response.py) (3835 chars)
- [backend/app/core/exceptions.py](/app#repo?file=backend/app/core/exceptions.py) (5541 chars)
- [backend/app/middleware/__init__.py](/app#repo?file=backend/app/middleware/__init__.py) (163 chars)
- [backend/app/middleware/exception_handler.py](/app#repo?file=backend/app/middleware/exception_handler.py) (6379 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (2259 chars)

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

### backend/app/schemas/response.py (新建, 3835 chars)
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

### backend/app/core/exceptions.py (新建, 5541 chars)
```
+ from typing import Optional
+ from fastapi import HTTPException, status
+ 
+ 
+ class BaseAPIException(HTTPException):
+     """Base exception for all API exceptions"""
+     
+     def __init__(
+         self,
+         status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
+         message: str = "Internal server error",
+         code: str = "INTERNAL_ERROR",
+         data: Optional[dict] = None
+     ):
+         self.status_code = status_code
+         self.message = message
+         self.code = code
+         self.data = data
+         super().__init__(status_code=status_code, detail=message)
+ 
+ ... (更多)
```

### backend/app/middleware/__init__.py (新建, 163 chars)
```
+ from .exception_handler import exception_handler_middleware, register_exception_handlers
+ 
+ __all__ = ["exception_handler_middleware", "register_exception_handlers"]
```

### backend/app/middleware/exception_handler.py (新建, 6379 chars)
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
+ from app.schemas.response import ResponseModel
+ from app.core.exceptions import (
+     BusinessException,
+     NotFoundException,
+     ValidationException,
+     UnauthorizedException,
+     ForbiddenException,
+     ConflictException,
+ )
+ 
+ logger = logging.getLogger(__name__)
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

 from backend.app.core.database import init_db, close_db

 from backend.app.routers import auth

@@ -26,6 +27,26 @@
     allow_headers=["*"],

 )

 

+

+# Exception handler middleware

+@app.middleware("http")

+async def exception_handler_middleware(request: Request, call_next):

+    """Catch all exceptions and return unified response format."""

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

 

@@ -49,7 +70,7 @@
 @app.get("/")

 async def root():

     """Health check endpoint."""

-    return {"status": "ok", "app": settings.APP_NAME}

+    return {"success": True, "message": "ok", "data": {"app": settings.APP_NAME}}

 

 

 if __name__ == "__main__":

```
