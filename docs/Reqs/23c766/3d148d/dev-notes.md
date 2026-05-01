# 开发笔记 — Frontend: Add data backup and restore UI

> 2026-05-02 01:37 | LLM

## 产出文件
- [backend/requirements.txt](/app#repo?file=backend/requirements.txt) (51 chars)
- [backend/pytest.ini](/app#repo?file=backend/pytest.ini) (315 chars)
- [backend/tests/__init__.py](/app#repo?file=backend/tests/__init__.py) (219 chars)
- [backend/tests/test_health.py](/app#repo?file=backend/tests/test_health.py) (1275 chars)
- [backend/run.sh](/app#repo?file=backend/run.sh) (313 chars)
- [backend/.gitignore](/app#repo?file=backend/.gitignore) (475 chars)
- [backend/main.py](/app#repo?file=backend/main.py) (15915 chars)
- [frontend/index.html](/app#repo?file=frontend/index.html) (29341 chars)

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

### backend/pytest.ini (新建, 315 chars)
```
+ [pytest]
+ testpaths = tests
+ python_files = test_*.py
+ python_classes = Test*
+ python_functions = test_*
+ addopts = 
+     -v
+     --strict-markers
+     --tb=short
+     --cov=app
+     --cov-report=term-missing
+     --cov-report=html
+ markers =
+     unit: Unit tests
+     integration: Integration tests
+     slow: Slow running tests
```

### backend/tests/__init__.py (新建, 219 chars)
```
+ """
+ Tests package initialization.
+ This file makes the tests directory a Python package.
+ """
+ 
+ # This file can be empty or contain shared test fixtures and utilities
+ # For now, we'll keep it minimal
+ 
+ __version__ = "1.0.0"
```

### backend/tests/test_health.py (新建, 1275 chars)
```
+ import pytest
+ from fastapi.testclient import TestClient
+ from backend.main import app
+ 
+ client = TestClient(app)
+ 
+ 
+ def test_health_check():
+     """测试健康检查端点"""
+     response = client.get("/health")
+     assert response.status_code == 200
+     assert response.json() == {"status": "healthy"}
+ 
+ 
+ def test_root_endpoint():
+     """测试根路径端点"""
+     response = client.get("/")
+     assert response.status_code == 200
+     data = response.json()
+     assert "message" in data
+ ... (更多)
```

### backend/run.sh (新建, 313 chars)
```
+ #!/bin/bash
+ 
+ # 启动后端服务
+ cd "$(dirname "$0")"
+ 
+ # 检查 Python 环境
+ if ! command -v python3 &> /dev/null; then
+     echo "错误: 未找到 python3，请先安装 Python 3"
+     exit 1
+ fi
+ 
+ # 检查依赖
+ if ! python3 -c "import flask" 2>/dev/null; then
+     echo "正在安装依赖..."
+     pip3 install flask flask-cors
+ fi
+ 
+ # 启动服务
+ echo "正在启动后端服务..."
+ python3 app.py
```

### backend/.gitignore (新建, 475 chars)
```
+ # Python
+ __pycache__/
+ *.py[cod]
+ *$py.class
+ *.so
+ .Python
+ build/
+ develop-eggs/
+ dist/
+ downloads/
+ eggs/
+ .eggs/
+ lib/
+ lib64/
+ parts/
+ sdist/
+ var/
+ wheels/
+ *.egg-info/
+ .installed.cfg
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

-/* ... [文件截断显示：原文 15915 字符，当前只显示前 15000；代码本身完整，保留未显示部分] ... */
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
@@ -205,9 +205,47 @@
             margin: 8px 0;

         }

 

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

+            gap: 10px;

+            margin-bottom: 20px;

+        }

+

+        .backup-buttons .btn {

+            flex: 1;

+        }

+

+        .btn-secondary {

+            background: #5f6368;

+        }

+

+        .btn-secondary:hover {

+            background: #3c4043;

+        }

+

+        input[type="file"] {

+            display: none;

+        }

+

         @media (max-width: 768px) {

             .auth-card {

                 padding: 24px;

+            }

+

+            .backup-buttons {

+                flex-direction: column;

             }

         }

     </style>

... (共 389 行变更)
```
