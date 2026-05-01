# 开发笔记 — Design bill query API schema and database indexes

> 2026-05-02 01:07 | LLM

## 产出文件
- [backend/app.py](/app#repo?file=backend/app.py) (2895 chars)
- [frontend/index.html](/app#repo?file=frontend/index.html) (15394 chars)

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

### backend/app.py (修改)
```diff
--- a/backend/app.py
+++ b/backend/app.py
@@ -6,6 +6,7 @@
 from backend.api.export import export_bp

 from backend.api.import_data import import_bp

 from backend.api.clear import clear_bp

+from backend.api.bills import bills_bp

 

 # Configure logging

 logging.basicConfig(

@@ -21,6 +22,7 @@
 app.register_blueprint(export_bp)

 app.register_blueprint(import_bp)

 app.register_blueprint(clear_bp)

+app.register_blueprint(bills_bp)

 

 # Initialize database

 init_db()

@@ -106,4 +108,4 @@
 

 if __name__ == '__main__':

     port = int(os.getenv('PORT', 8080))

-    app.run(host='0.0.0.0', port=port, debug=True)

+    app.run(host='0.0.0.0', port=port, debug=True)
```

### frontend/index.html (修改)
```diff
--- a/frontend/index.html
+++ b/frontend/index.html
@@ -192,6 +192,91 @@
       display: none;

     }

     

+    .query-filters {

+      background: rgba(255,255,255,0.05);

+      border-radius: 8px;

+      padding: 20px;

+      margin-bottom: 20px;

+    }

+    

+    .filter-row {

+      display: flex;

+      gap: 15px;

+      flex-wrap: wrap;

+      align-items: flex-end;

+    }

+    

+    .filter-group {

+      flex: 1;

+      min-width: 200px;

+    }

+    

+    .filter-group label {

+      display: block;

+      margin-bottom: 5px;

+      font-size: 0.9rem;

+      opacity: 0.8;

+    }

+    

+    .filter-group input,

+    .filter-group select {

+      width: 100%;

+      padding: 10px;

+      border: 1px solid var(--border);

+      border-radius: 6px;

+      background: var(--secondary);

+      color: var(--text);

+      font-size: 1rem;

+    }

+    

+    .filter-group input:focus,

+    .filter-group select:focus {

+      outline: none;

+      border-color: var(--highlight);

+    }

+    

+    .btn-filter {

... (共 257 行变更)
```
