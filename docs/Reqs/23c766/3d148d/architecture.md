# 架构设计 - Frontend: Add data backup and restore UI

## 架构模式
Frontend UI Extension

## 技术栈

- **frontend**: {'framework': 'HTML/JavaScript (Vanilla or existing framework)', 'http_client': 'Fetch API', 'ui_components': 'Native HTML elements (button, input[type=file], dialog/modal)'}
- **integration**: {'backend_apis': ['GET /api/export', 'POST /api/import', 'DELETE /api/clear'], 'file_handling': 'Browser File API (download/upload)'}

## 模块设计

### 
职责: 

### 
职责: 

### 
职责: 

## 关键决策
- {'decision': 'Use native HTML file input instead of drag-drop', 'rationale': 'Simpler implementation, better browser compatibility, sufficient for backup/restore use case'}
- {'decision': 'Filename format: visits_backup_YYYYMMDD_HHMMSS.json', 'rationale': 'Clear naming convention, sortable by date, avoids filename conflicts'}
- {'decision': 'Use browser confirm() for double confirmation', 'rationale': 'Native dialog is blocking and ensures user attention, can be upgraded to custom modal later if needed'}
- {'decision': 'Display import result with success/failure counts', 'rationale': 'Provides transparency on partial import scenarios, helps user understand what happened'}
- {'decision': 'Refresh visit counter after import/clear operations', 'rationale': 'Ensures UI reflects latest data state immediately after data modification'}
- {'decision': 'Set MAX_CONTENT_LENGTH to 16MB in Flask app', 'rationale': 'Already configured in backend/app.py, sufficient for typical visit data exports'}
