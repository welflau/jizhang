# 开发笔记 — Frontend: Add data backup and restore UI

> 2026-05-02 01:30 | LLM

## 产出文件
- [backend/app/api/v1/endpoints/data_management.py](/app#repo?file=backend/app/api/v1/endpoints/data_management.py) (4425 chars)
- [backend/app/schemas/data_management.py](/app#repo?file=backend/app/schemas/data_management.py) (1352 chars)
- [backend/app/services/data_management.py](/app#repo?file=backend/app/services/data_management.py) (6747 chars)
- [tests/integration/test_data_management_flow.py](/app#repo?file=tests/integration/test_data_management_flow.py) (10836 chars)
- [frontend/components/DataManagement.js](/app#repo?file=frontend/components/DataManagement.js) (4432 chars)
- [backend/main.py](/app#repo?file=backend/main.py) (15915 chars)
- [frontend/index.html](/app#repo?file=frontend/index.html) (25038 chars)

## 自测: 自测 7/7 通过 ✅

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 7 个文件 |
| 入口文件 | ✅ | 存在 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 7 个文件已落盘 |
| 页面截图 | ✅ | 1 张截图 |

## 代码变更 (Diff)

### backend/app/api/v1/endpoints/data_management.py (新建, 4425 chars)
```
+ from fastapi import APIRouter, HTTPException, UploadFile, File
+ from fastapi.responses import StreamingResponse
+ from sqlalchemy.orm import Session
+ from typing import List
+ import json
+ import io
+ from datetime import datetime
+ 
+ from app.db.session import get_db
+ from app.models.visit import Visit
+ from app.schemas.visit import VisitCreate
+ 
+ router = APIRouter()
+ 
+ 
+ @router.get("/export")
+ def export_data(db: Session = next(get_db())):
+     """
+     导出所有访问记录为 JSON 文件
+     """
+ ... (更多)
```

### backend/app/schemas/data_management.py (新建, 1352 chars)
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
+     remarks: Optional[str] = None
+     created_at: datetime
+ ... (更多)
```

### backend/app/services/data_management.py (新建, 6747 chars)
```
+ import json
+ import logging
+ from datetime import datetime
+ from typing import Dict, List, Any
+ from sqlalchemy.orm import Session
+ from app.models.visit import Visit
+ 
+ logger = logging.getLogger(__name__)
+ 
+ 
+ class DataManagementService:
+     """数据管理服务：负责数据的导出、导入和清空操作"""
+ 
+     @staticmethod
+     def export_data(db: Session) -> Dict[str, Any]:
+         """
+         导出所有访问记录数据
+         
+         Args:
+             db: 数据库会话
+ ... (更多)
```

### tests/integration/test_data_management_flow.py (新建, 10836 chars)
```
+ import pytest
+ import json
+ import io
+ from datetime import datetime
+ from flask import Flask
+ from app import app, db, Visit
+ 
+ 
+ @pytest.fixture
+ def client():
+     """创建测试客户端"""
+     app.config['TESTING'] = True
+     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
+     
+     with app.test_client() as client:
+         with app.app_context():
+             db.create_all()
+             yield client
+             db.session.remove()
+             db.drop_all()
+ ... (更多)
```

### frontend/components/DataManagement.js (新建, 4432 chars)
```
+ import React, { useState } from 'react';
+ import { Card, Button, Upload, message, Modal, Space, Typography, Divider } from 'antd';
+ import { DownloadOutlined, UploadOutlined, DeleteOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
+ import axios from 'axios';
+ 
+ const { Title, Text } = Typography;
+ const { confirm } = Modal;
+ 
+ const DataManagement = () => {
+   const [importing, setImporting] = useState(false);
+   const [exporting, setExporting] = useState(false);
+ 
+   // 导出数据
+   const handleExport = async () => {
+     try {
+       setExporting(true);
+       const response = await axios.get('/api/export', {
+         responseType: 'blob'
+       });
+       
+ ... (更多)
```

### backend/main.py (修改)
```diff
--- a/backend/main.py
+++ b/backend/main.py
@@ -433,6 +433,27 @@
     """Delete a backup file"""

     try:

         # Validate filename to prevent path traversal

-        if ".." 

-

-/* ... [文件截断显示：原文 16118 字符，当前只显示前 15000；代码本身完整，保留未显示部分] ... */
+        if ".." in filename or "/" in filename or "\\" in filename:

+            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")

+        

+        backup_path = os.path.join(BACKUP_DIR, filename)

+        

+        if not os.path.exists(backup_path):

+            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup file not found")

+        

+        # Delete the backup file

+        os.remove(backup_path)

+        

+        logger.info(f"Backup deleted by user {current_user['email']}: {filename}")

+        

+        return {"message": "Backup deleted successfully"}

+    except HTTPException:

+        raise

+    except Exception as e:

+        logger.error(f"Delete failed: {e}")

+        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Delete failed")

+

+

+if __name__ == "__main__":

+    import uvicorn

+    uvicorn.run(app, host="0.0.0.0", port=PORT)
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

@@ -210,6 +211,29 @@
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

+            text-align: center;

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

@@ -289,6 +313,7 @@
                             <p><strong>Member since:</strong> {new Date(user.created_at).toLocaleDateString()}</p>

                             <button onClick={handleLogout} style={{marginTop: '20px'}}>Logout</button>

                         </div>

+                        <BackupSection token={token} />

                     </div>

                 );

             }

... (共 302 行变更)
```

## 页面预览截图

![开发自测 — Frontend: Add data backup and ](screenshots/dev_1777656653.png)

