# 开发笔记 — Implement JWT authentication middleware

> 2026-05-02 01:28 | LLM

## 产出文件
- [backend/.env.example](/app#repo?file=backend/.env.example) (1066 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (1675 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 2 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 2 个文件已落盘 |

## 代码变更 (Diff)

### backend/.env.example (新建, 1066 chars)
```
+ # Application Settings
+ APP_NAME=MyApp
+ APP_VERSION=1.0.0
+ DEBUG=True
+ ENVIRONMENT=development
+ 
+ # Server Configuration
+ HOST=0.0.0.0
+ PORT=8000
+ 
+ # Database Configuration
+ DATABASE_URL=postgresql://user:password@localhost:5432/dbname
+ DATABASE_ECHO=False
+ 
+ # JWT Authentication Settings
+ JWT_SECRET_KEY=your-secret-key-here-change-in-production
+ JWT_ALGORITHM=HS256
+ JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
+ JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
+ 
+ ... (更多)
```

### backend/app/main.py (修改)
```diff
--- a/backend/app/main.py
+++ b/backend/app/main.py
@@ -2,6 +2,7 @@
 from fastapi.middleware.cors import CORSMiddleware

 from backend.app.core.config import settings

 from backend.app.core.database import init_db, close_db

+from backend.app.core.middleware import JWTAuthMiddleware

 from backend.app.routers import auth

 import logging

 

@@ -25,6 +26,9 @@
     allow_methods=["*"],

     allow_headers=["*"],

 )

+

+# JWT authentication middleware

+app.add_middleware(JWTAuthMiddleware)

 

 # Include routers

 app.include_router(auth.router)

```
