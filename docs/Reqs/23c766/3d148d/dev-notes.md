# 开发笔记 — Frontend: Add data backup and restore UI

> 2026-05-02 01:29 | LLM

## 产出文件
- [backend/app/api/v1/endpoints/data_management.py](/app#repo?file=backend/app/api/v1/endpoints/data_management.py) (5141 chars)
- [backend/app/schemas/data_management.py](/app#repo?file=backend/app/schemas/data_management.py) (1339 chars)
- [tests/test_data_management.py](/app#repo?file=tests/test_data_management.py) (11257 chars)
- [frontend/index.html](/app#repo?file=frontend/index.html) (25080 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (2001 chars)

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

### backend/app/api/v1/endpoints/data_management.py (新建, 5141 chars)
```
+ from fastapi import APIRouter, HTTPException, UploadFile, File
+ from fastapi.responses import StreamingResponse
+ from sqlalchemy.orm import Session
+ from typing import List
+ import json
+ import io
+ from datetime import datetime
+ 
+ from app.api import deps
+ from app.models.visit import Visit
+ from app.schemas.visit import VisitCreate
+ 
+ router = APIRouter()
+ 
+ 
+ @router.get("/export")
+ def export_data(db: Session = deps.Depends(deps.get_db)):
+     """
+     导出所有访问记录为 JSON 文件
+     """
+ ... (更多)
```

### backend/app/schemas/data_management.py (新建, 1339 chars)
```
+ from pydantic import BaseModel, Field
+ from typing import List, Optional
+ from datetime import datetime
+ 
+ 
+ class VisitRecordExport(BaseModel):
+     """导出的访问记录模型"""
+     id: int
+     visitor_name: str
+     company: Optional[str] = None
+     phone: str
+     id_card: Optional[str] = None
+     visit_purpose: str
+     host_name: str
+     host_department: Optional[str] = None
+     visit_time: datetime
+     leave_time: Optional[datetime] = None
+     status: str
+     notes: Optional[str] = None
+     created_at: datetime
+ ... (更多)
```

### tests/test_data_management.py (新建, 11257 chars)
```
+ import pytest
+ import json
+ from datetime import datetime
+ from app import app, db, Visit
+ 
+ @pytest.fixture
+ def client():
+     app.config['TESTING'] = True
+     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
+     
+     with app.test_client() as client:
+         with app.app_context():
+             db.create_all()
+             yield client
+             db.session.remove()
+             db.drop_all()
+ 
+ @pytest.fixture
+ def sample_visits(client):
+     """创建测试数据"""
+ ... (更多)
```

### frontend/index.html (修改)
```diff
--- a/frontend/index.html
+++ b/frontend/index.html
@@ -69,7 +69,8 @@
 

         input[type="email"],

         input[type="password"],

-        input[type="tel"] {

+        input[type="tel"],

+        input[type="file"] {

             width: 100%;

             padding: 12px 16px;

             border: 1px solid var(--border);

@@ -210,6 +211,28 @@
             background: #e6f4ea;

             color: var(--success);

             border: 1px solid #c3e6cb;

+        }

+

+        .backup-section {

+            margin-top: 30px;

+            padding-top: 30px;

+            border-top: 1px solid var(--border);

+        }

+

+        .backup-section h3 {

+            color: var(--text-primary);

+            font-size: 18px;

+            margin-bottom: 20px;

+        }

+

+        .backup-buttons {

+            display: flex;

+            flex-direction: column;

+            gap: 10px;

+        }

+

+        .backup-buttons button {

+            margin: 0;

         }

 

         @media (max-width: 768px) {

@@ -289,6 +312,7 @@
                             <p><strong>Member since:</strong> {new Date(user.created_at).toLocaleDateString()}</p>

                             <button onClick={handleLogout} style={{marginTop: '20px'}}>Logout</button>

                         </div>

+                        <BackupSection token={token} />

                     </div>

                 );

             }

@@ -462,6 +486,249 @@
... (共 302 行变更)
```

### backend/app/main.py (修改)
```diff
--- a/backend/app/main.py
+++ b/backend/app/main.py
@@ -3,7 +3,7 @@
 from fastapi.responses import JSONResponse

 from backend.app.core.config import settings

 from backend.app.core.database import init_db

-from backend.app.routers import auth

+from backend.app.routers import auth, backup

 import logging

 

 # Configure logging

@@ -49,6 +49,7 @@
 

 # Include routers

 app.include_router(auth.router)

+app.include_router(backup.router)

 

 

 @app.on_event("startup")

```
