# 开发笔记 — Backend: Implement data export/import/clear APIs

> 2026-05-02 01:01 | LLM

## 产出文件
- [backend/api/export.py](/app#repo?file=backend/api/export.py) (1768 chars)
- [backend/api/import_data.py](/app#repo?file=backend/api/import_data.py) (4444 chars)
- [backend/api/clear.py](/app#repo?file=backend/api/clear.py) (2190 chars)
- [backend/app.py](/app#repo?file=backend/app.py) (2824 chars)
- [backend/database.py](/app#repo?file=backend/database.py) (1298 chars)
- [frontend/index.html](/app#repo?file=frontend/index.html) (9988 chars)
- [requirements.txt](/app#repo?file=requirements.txt) (32 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 7 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 7 个文件已落盘 |

## 代码变更 (Diff)

### backend/api/export.py (新建, 1768 chars)
```
+ """Export API endpoint for visitor records."""
+ import json
+ import logging
+ from flask import Blueprint, jsonify, Response
+ from backend.database import get_db_connection
+ 
+ logger = logging.getLogger(__name__)
+ export_bp = Blueprint('export', __name__)
+ 
+ 
+ @export_bp.route('/api/export', methods=['GET'])
+ def export_records():
+     """Export all visitor records as JSON file.
+     
+     Returns:
+         JSON file download with all records sorted by timestamp.
+     """
+     try:
+         conn = get_db_connection()
+         cursor = conn.cursor()
+ ... (更多)
```

### backend/api/import_data.py (新建, 4444 chars)
```
+ """Import API endpoint for visitor records."""
+ import json
+ import logging
+ from flask import Blueprint, request, jsonify
+ from jsonschema import validate, ValidationError
+ from backend.database import get_db_connection
+ 
+ logger = logging.getLogger(__name__)
+ import_bp = Blueprint('import_data', __name__)
+ 
+ # JSON schema for validation
+ RECORD_SCHEMA = {
+     "type": "array",
+     "items": {
+         "type": "object",
+         "required": ["timestamp", "ip"],
+         "properties": {
+             "id": {"type": "integer"},
+             "timestamp": {"type": "string"},
+             "ip": {"type": "string"},
+ ... (更多)
```

### backend/api/clear.py (新建, 2190 chars)
```
+ """Clear API endpoint for visitor records."""
+ import logging
+ from flask import Blueprint, request, jsonify
+ from backend.database import get_db_connection
+ 
+ logger = logging.getLogger(__name__)
+ clear_bp = Blueprint('clear', __name__)
+ 
+ # Simple token-based authentication (should be in env var in production)
+ CLEAR_TOKEN = "dev_clear_token_12345"
+ 
+ 
+ def verify_clear_token(token):
+     """Verify clear operation token.
+     
+     Args:
+         token: Token from request header
+         
+     Returns:
+         bool: True if valid
+ ... (更多)
```

### backend/app.py (新建, 2824 chars)
```
+ """Main Flask application with visitor tracking and data management APIs."""
+ import os
+ import logging
+ from flask import Flask, request, jsonify
+ from backend.database import init_db, get_db_connection
+ from backend.api.export import export_bp
+ from backend.api.import_data import import_bp
+ from backend.api.clear import clear_bp
+ 
+ # Configure logging
+ logging.basicConfig(
+     level=logging.INFO,
+     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
+ )
+ logger = logging.getLogger(__name__)
+ 
+ app = Flask(__name__)
+ app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
+ 
+ # Register blueprints
+ ... (更多)
```

### backend/database.py (新建, 1298 chars)
```
+ """Database initialization and connection management."""
+ import sqlite3
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ DB_PATH = 'visitor_data.db'
+ 
+ 
+ def get_db_connection():
+     """Get SQLite database connection.
+     
+     Returns:
+         sqlite3.Connection: Database connection with row factory
+     """
+     conn = sqlite3.connect(DB_PATH, timeout=5.0)
+     conn.row_factory = sqlite3.Row
+     return conn
+ 
+ 
+ def init_db():
+ ... (更多)
```

### frontend/index.html (新建, 9988 chars)
```
+ <!DOCTYPE html>
+ <html lang="zh-CN">
+ <head>
+   <meta charset="UTF-8">
+   <meta name="viewport" content="width=device-width, initial-scale=1.0">
+   <title>访客追踪系统</title>
+   <style>
+     * {
+       box-sizing: border-box;
+       margin: 0;
+       padding: 0;
+     }
+     
+     :root {
+       --primary: #1a1a2e;
+       --secondary: #16213e;
+       --accent: #0f3460;
+       --highlight: #e94560;
+       --text: #eee;
+       --border: #444;
+ ... (更多)
```
