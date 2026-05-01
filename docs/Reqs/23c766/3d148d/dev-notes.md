# 开发笔记 — Frontend: Add data backup and restore UI

> 2026-05-02 01:35 | LLM

## 产出文件
- [backend/startup_test.sh](/app#repo?file=backend/startup_test.sh) (723 chars)
- [backend/main.py](/app#repo?file=backend/main.py) (15915 chars)

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

### backend/startup_test.sh (新建, 723 chars)
```
+ #!/bin/bash
+ 
+ # 启动测试脚本 - 用于验证数据备份和恢复功能
+ 
+ set -e
+ 
+ echo "=========================================="
+ echo "启动后端服务测试"
+ echo "=========================================="
+ 
+ # 检查 Python 环境
+ if ! command -v python3 &> /dev/null; then
+     echo "错误: 未找到 python3"
+     exit 1
+ fi
+ 
+ # 检查依赖
+ echo "检查依赖..."
+ python3 -c "import flask" 2>/dev/null || { echo "错误: 未安装 flask"; exit 1; }
+ python3 -c "import flask_cors" 2>/dev/null || { echo "错误: 未安装 flask-cors"; exit 1; }
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
