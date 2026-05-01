# 开发笔记 — Backend: Implement data export/import/clear APIs

> 2026-05-02 01:00 | LLM

## 产出文件
- [api/data_management.py](/app#repo?file=api/data_management.py) (4128 chars)
- [services/data_service.py](/app#repo?file=services/data_service.py) (6294 chars)
- [utils/validators.py](/app#repo?file=utils/validators.py) (2339 chars)
- [app.py](/app#repo?file=app.py) (2638 chars)
- [index.html](/app#repo?file=index.html) (12434 chars)
- [requirements.txt](/app#repo?file=requirements.txt) (29 chars)

## 自测: 自测 6/6 通过 ✅

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 6 个文件 |
| 入口文件 | ✅ | 存在 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 6 个文件已落盘 |

## 代码变更 (Diff)

### api/data_management.py (新建, 4128 chars)
```
+ from flask import Blueprint, jsonify, request, send_file
+ from services.data_service import DataService
+ from utils.validators import validate_import_data
+ import logging
+ import io
+ import json
+ 
+ logger = logging.getLogger(__name__)
+ data_bp = Blueprint('data_management', __name__)
+ data_service = DataService()
+ 
+ 
+ @data_bp.route('/api/export', methods=['GET'])
+ def export_data():
+     """
+     Export all visit records as JSON file.
+     Returns downloadable JSON file with all records sorted by timestamp.
+     """
+     try:
+         records = data_service.export_all_records()
+ ... (更多)
```

### services/data_service.py (新建, 6294 chars)
```
+ import sqlite3
+ import logging
+ from typing import List, Dict, Any
+ from datetime import datetime
+ 
+ logger = logging.getLogger(__name__)
+ 
+ 
+ class DataService:
+     """
+     Service layer for data management operations.
+     Handles export, import, and clear operations with proper transaction management.
+     """
+     
+     def __init__(self, db_path: str = 'visits.db'):
+         self.db_path = db_path
+     
+     def _get_connection(self) -> sqlite3.Connection:
+         """Create database connection with row factory."""
+         conn = sqlite3.connect(self.db_path)
+ ... (更多)
```

### utils/validators.py (新建, 2339 chars)
```
+ from typing import Dict, List, Any
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
+ 
+ def validate_import_data(records: Any) -> Dict[str, Any]:
+     """
+     Validate imported data structure and content.
+     
+     Args:
+         records: Data to validate (should be list of dicts)
+         
+     Returns:
+         Dictionary with 'valid' boolean and 'errors' list
+     """
+     result = {
+         'valid': True,
+         'errors': []
+     }
+ ... (更多)
```

### app.py (新建, 2638 chars)
```
+ from flask import Flask, request, jsonify
+ import sqlite3
+ import logging
+ from datetime import datetime
+ from api.data_management import data_bp
+ 
+ app = Flask(__name__, static_folder='.', static_url_path='')
+ app.register_blueprint(data_bp)
+ 
+ # Configure logging
+ logging.basicConfig(
+     level=logging.INFO,
+     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
+ )
+ logger = logging.getLogger(__name__)
+ 
+ DB_PATH = 'visits.db'
+ 
+ 
+ def init_db():
+ ... (更多)
```

### index.html (新建, 12434 chars)
```
+ <!DOCTYPE html>
+ <html lang="zh-CN">
+ <head>
+     <meta charset="UTF-8">
+     <meta name="viewport" content="width=device-width, initial-scale=1.0">
+     <title>访问统计系统</title>
+     <style>
+         * {
+             box-sizing: border-box;
+             margin: 0;
+             padding: 0;
+         }
+         
+         :root {
+             --primary: #1a1a2e;
+             --secondary: #16213e;
+             --accent: #0f3460;
+             --highlight: #e94560;
+             --text: #f1f1f1;
+         }
+ ... (更多)
```
