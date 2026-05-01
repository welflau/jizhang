# Access Log API Backend

## Features

- **Export**: Download all access logs as JSON file
- **Import**: Upload and batch insert access logs from JSON file
- **Clear**: Delete all access logs (requires admin token)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and set ADMIN_TOKEN to a secure random string
```

3. Run the server:
```bash
python -m app.main
```

Server will start on `http://0.0.0.0:8080`

## API Endpoints

### GET /api/export
Export all access records as JSON file.

**Response**: JSON array sorted by timestamp (descending)
```json
[
  {
    "id": 2,
    "timestamp": "2024-01-01T11:00:00",
    "ip": "192.168.1.2",
    "user_agent": "Chrome/120",
    "path": "/about"
  }
]
```

### POST /api/import
Import access records from JSON file.

**Request**: multipart/form-data with `file` field

**Response**:
```json
{
  "success": true,
  "imported_count": 10,
  "skipped_count": 2,
  "errors": ["Record ID 5 already exists, skipped"]
}
```

**Validation Rules**:
- JSON must be an array of objects
- Each record must have: `id` (positive integer), `timestamp` (ISO format), `ip` (7-45 chars)
- Duplicate IDs are skipped
- Invalid timestamps are skipped

### POST /api/clear
Clear all access records (requires admin token).

**Headers**:
```
Authorization: Bearer <ADMIN_TOKEN>
```

**Response**:
```json
{
  "success": true,
  "deleted": 42
}
```

**Error Responses**:
- `401`: Missing or invalid admin token
- `500`: Database operation failed

## Security

- Clear endpoint requires `ADMIN_TOKEN` environment variable
- Token must be passed as `Bearer <token>` in Authorization header
- **Never commit `.env` file to version control**
- Use strong random tokens in production (e.g., `openssl rand -hex 32`)

## Testing

Run tests with pytest:
```bash
pytest backend/tests/test_export_import_clear.py -v
```

Tests cover:
- Export format and sorting
- Import validation and duplicate handling
- Clear authorization and deletion count
- Error scenarios (invalid JSON, missing token, etc.)

## Database Schema

```sql
CREATE TABLE access_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    ip TEXT NOT NULL,
    user_agent TEXT,
    path TEXT
);
CREATE INDEX idx_timestamp ON access_logs(timestamp);
```

## Logging

All operations are logged with:
- INFO: Successful operations (export count, import stats, clear count)
- WARNING: Unauthorized access attempts
- ERROR: Database failures, validation errors

Logs include timestamps and request details for audit trail.
