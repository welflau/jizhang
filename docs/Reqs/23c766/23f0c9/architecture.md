# 架构设计 - Backend: Implement data export/import/clear APIs

## 架构模式
RESTful API Extension

## 技术栈

- **framework**: Flask (existing)
- **database**: SQLite (existing)
- **serialization**: json (built-in)
- **validation**: jsonschema
- **transaction**: sqlite3.Connection context manager
- **logging**: logging (built-in)

## 模块设计

### 
职责: Export endpoint implementation
- input
- output

### 
职责: Import endpoint implementation
- input
- output

### 
职责: Clear endpoint implementation
- input
- output

### 
职责: Data validation utilities
- input
- output

### 
职责: Database operation helpers
- input
- output

## 关键决策
- {'decision': 'Use JSON schema validation instead of manual checks', 'rationale': 'Ensures consistent validation logic, easier to maintain and extend schema', 'alternatives': 'Manual field checking (error-prone, harder to maintain)'}
- {'decision': 'Import uses SKIP strategy for duplicate IDs by default', 'rationale': 'Safer than overwrite, prevents accidental data loss, user can clear first if needed', 'alternatives': 'UPDATE on conflict (risky), ABORT on duplicate (poor UX)'}
- {'decision': 'Clear endpoint requires confirmation_token from frontend', 'rationale': 'Prevents accidental deletion via CSRF or misclick, token generated per session', 'alternatives': 'Admin password (harder UX), no protection (dangerous)'}
- {'decision': 'Export returns file as attachment with timestamp in filename', 'rationale': 'Browser auto-downloads, filename includes export time for version tracking', 'alternatives': 'Inline JSON (requires manual save), fixed filename (overwrite risk)'}
- {'decision': 'All operations use database transactions', 'rationale': 'Guarantees atomicity - import/clear either fully succeeds or fully rolls back', 'alternatives': 'No transaction (partial failure leaves inconsistent state)'}
