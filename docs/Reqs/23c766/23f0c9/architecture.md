# 架构设计 - Backend: Implement data export/import/clear APIs

## 架构模式
RESTful API Extension

## 技术栈

- **framework**: Flask (existing)
- **database**: SQLite (existing)
- **serialization**: json (built-in)
- **file_handling**: werkzeug.datastructures.FileStorage
- **transaction**: sqlite3 context manager
- **validation**: jsonschema

## 模块设计

### 
职责: 
- GET /api/export -> returns JSON file download
- POST /api/import -> accepts multipart/form-data with JSON file
- POST /api/clear -> accepts confirmation token, returns deletion count

### 
职责: 

### 
职责: 

### 
职责: 

## 关键决策
- {'decision': 'Use JSON Schema for import validation', 'rationale': 'Ensures data integrity before database operations, prevents malformed data injection'}
- {'decision': 'Implement token-based confirmation for clear operation', 'rationale': 'Prevents accidental data loss from CSRF or misclicks; token expires after 5 minutes'}
- {'decision': 'Handle duplicate IDs by skipping (not overwriting)', 'rationale': 'Preserves existing data integrity; returns skipped count for user awareness'}
- {'decision': 'Export uses streaming response for large datasets', 'rationale': 'Prevents memory overflow when record count exceeds thousands'}
- {'decision': 'Import uses batch insert with transaction rollback', 'rationale': "All-or-nothing semantics; partial failure doesn't corrupt database"}
- {'decision': 'Add rate limiting to clear endpoint (1 req/minute)', 'rationale': 'Prevents abuse or accidental repeated deletions'}
