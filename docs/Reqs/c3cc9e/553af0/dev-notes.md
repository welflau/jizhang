# 开发笔记 — Create unified response format and exception handler middleware

> 2026-05-02 01:32 | LLM

## 产出文件
- [backend/app/schemas/response.py](/app#repo?file=backend/app/schemas/response.py) (3770 chars)
- [backend/app/middleware/__init__.py](/app#repo?file=backend/app/middleware/__init__.py) (231 chars)
- [backend/app/middleware/exception_handler.py](/app#repo?file=backend/app/middleware/exception_handler.py) (5116 chars)
- [backend/app/exceptions/__init__.py](/app#repo?file=backend/app/exceptions/__init__.py) (525 chars)
- [backend/app/exceptions/business.py](/app#repo?file=backend/app/exceptions/business.py) (2314 chars)
- [backend/tests/__init__.py](/app#repo?file=backend/tests/__init__.py) (279 chars)
- [backend/tests/test_response_format.py](/app#repo?file=backend/tests/test_response_format.py) (7717 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (2238 chars)
- [frontend/index.html](/app#repo?file=frontend/index.html) (24276 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 9 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 9 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/schemas/response.py (新建, 3770 chars)
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

### backend/app/middleware/__init__.py (新建, 231 chars)
```
+ from app.middleware.exception_handler import exception_handler_middleware
+ from app.middleware.response_wrapper import response_wrapper_middleware
+ 
+ __all__ = [
+     "exception_handler_middleware",
+     "response_wrapper_middleware",
+ ]
```

### backend/app/middleware/exception_handler.py (新建, 5116 chars)
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
+     def __init__(self, message: str = "Internal Server Error", code: int = 500, data: any = None):
+         self.message = message
+         self.code = code
+         self.data = data
+         super().__init__(self.message)
+ 
+ ... (更多)
```

### backend/app/exceptions/__init__.py (新建, 525 chars)
```
+ from .base import (
+     AppException,
+     BadRequestException,
+     UnauthorizedException,
+     ForbiddenException,
+     NotFoundException,
+     ConflictException,
+     ValidationException,
+     InternalServerException,
+ )
+ from .handlers import register_exception_handlers
+ 
+ __all__ = [
+     "AppException",
+     "BadRequestException",
+     "UnauthorizedException",
+     "ForbiddenException",
+     "NotFoundException",
+     "ConflictException",
+     "ValidationException",
+ ... (更多)
```

### backend/app/exceptions/business.py (新建, 2314 chars)
```
+ from typing import Optional
+ 
+ 
+ class BusinessException(Exception):
+     """业务异常基类"""
+ 
+     def __init__(
+         self,
+         message: str = "Business error occurred",
+         code: int = 400,
+         data: Optional[dict] = None,
+     ):
+         self.message = message
+         self.code = code
+         self.data = data
+         super().__init__(self.message)
+ 
+ 
+ class NotFoundError(BusinessException):
+     """资源未找到异常"""
+ ... (更多)
```

### backend/tests/__init__.py (新建, 279 chars)
```
+ # backend/tests/__init__.py
+ """
+ Tests package initialization.
+ Provides common test utilities and fixtures.
+ """
+ 
+ import sys
+ from pathlib import Path
+ 
+ # Add backend directory to Python path for imports
+ backend_dir = Path(__file__).parent.parent
+ sys.path.insert(0, str(backend_dir))
```

### backend/tests/test_response_format.py (新建, 7717 chars)
```
+ import pytest
+ from fastapi import FastAPI
+ from fastapi.testclient import TestClient
+ from app.schemas.response import ResponseModel, response_success, response_error
+ from app.middleware.exception_handler import (
+     NotFoundError,
+     ValidationError,
+     BusinessError,
+     AuthenticationError,
+     PermissionError,
+ )
+ 
+ 
+ @pytest.fixture
+ def app():
+     app = FastAPI()
+ 
+     @app.get("/success")
+     async def success_endpoint():
+         return response_success(data={"message": "success"})
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

@@ -25,6 +26,26 @@
     allow_methods=["*"],

     allow_headers=["*"],

 )

+

+

+# Global exception handler middleware

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

 

 # Include routers

 app.include_router(auth.router)

```

### frontend/index.html (修改)
```diff
--- a/frontend/index.html
+++ b/frontend/index.html
@@ -299,10 +299,10 @@
                     const data = await response.json();

 

                     if (!response.ok) {

-                        throw new Error(data.detail || 'Login failed');

+                        throw new Error(data.message || data.detail || 'Login failed');

                     }

 

-                    onSuccess(data.access_token, data.refresh_token);

+                    onSuccess(data.data.access_token, data.data.refresh_token);

                 } catch (err) {

                     setError(err.message);

                 } finally {

@@ -406,7 +406,7 @@
                     const data = await response.json();

 

                     if (!response.ok) {

-                        throw new Error(data.detail || 'Registration failed');

+                        throw new Error(data.message || data.detail || 'Registration failed');

                     }

 

                     setSuccess(true);

@@ -448,6 +448,219 @@
                                     id="password"

                                     type="password"

                                     value={password}

-                                    onChange={(e) => setPassword(e.target.value

-

-/* ... [文件截断显示：原文 19903 字符，当前只显示前 15000；代码本身完整，保留未显示部分] ... */
+                                    onChange={(e) => setPassword(e.target.value)}

+                                    required

+                                    placeholder="At least 8 characters"

+                                />

+                            </div>

+

+                            <div className="form-group">

+                                <label htmlFor="confirmPassword">Confirm Password</label>

+                                <input

+                                    id="confirmPassword"

+                                    type="password"

+                                    value={confirmPassword}

+                                    onChange={(e) => setConfirmPassword(e.target.value)}

+                                    required

+                                    placeholder="Confirm your password"

+                                />

+                            </div>

+

+                            <button type="submit" className="btn" disabled={loading}>

... (共 247 行变更)
```
