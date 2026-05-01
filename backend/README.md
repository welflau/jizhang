# User Information Update API

## Overview

Backend API for user information management with JWT authentication. Supports updating nickname, avatar, password, and user preferences with persistent storage.

## Features

- **User Profile Update**: Modify nickname and avatar
- **Password Change**: Secure password update with old password verification
- **Preferences Management**: Persistent storage of user preferences (theme, language, notifications)
- **JWT Authentication**: Token-based authentication for all endpoints
- **Input Validation**: Comprehensive validation using Pydantic v2
- **Async Operations**: Full async/await support with aiosqlite

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: SQLite (async via aiosqlite)
- **Authentication**: JWT (PyJWT)
- **Password Hashing**: bcrypt
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Environment Variables

```bash
# Required
JWT_SECRET=your-secret-key-change-in-production

# Optional
PORT=8080
ENV=development  # Enable auto-reload
```

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nickname TEXT,
    avatar TEXT,
    email TEXT,
    preferences TEXT DEFAULT '{}',  -- JSON string
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

## API Endpoints

### Get Current User

```http
GET /api/user/me
Authorization: Bearer <jwt_token>
```

**Response**:
```json
{
  "id": 1,
  "username": "johndoe",
  "nickname": "John Doe",
  "avatar": "https://example.com/avatar.jpg",
  "email": "john@example.com",
  "preferences": {"theme": "dark"},
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Update User Information

```http
PUT /api/user/update
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "nickname": "New Nickname",
  "avatar": "https://example.com/new-avatar.jpg",
  "old_password": "current_password",
  "new_password": "new_secure_password123",
  "preferences": {
    "theme": "dark",
    "language": "en-US",
    "notifications_enabled": true
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "User information updated successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "nickname": "New Nickname",
    "avatar": "https://example.com/new-avatar.jpg",
    "preferences": {"theme": "dark", "language": "en-US"}
  }
}
```

### Update Preferences (Merge)

```http
PATCH /api/user/preferences
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "theme": "dark"
}
```

Merges with existing preferences without overwriting other keys.

## Validation Rules

### Nickname
- Length: 2-30 characters
- Allowed: Letters, numbers, Chinese characters, spaces, hyphens
- Pattern: `^[\w\u4e00-\u9fa5\s-]+$`

### Avatar
- Must be valid URL (`http://`, `https://`) or base64 data URI (`data:image/`)
- Max length: 500 characters

### Password
- Min length: 6 characters
- Max length: 128 characters
- Must contain both letters and numbers
- Requires `old_password` verification when changing

### Preferences
- Stored as JSON string in database
- Supports nested objects
- Common fields:
  - `theme`: "light" | "dark"
  - `language`: "zh-CN" | "en-US" | etc.
  - `notifications_enabled`: boolean
  - `email_notifications`: boolean

## Running the Server

### Development Mode

```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Production Mode

```bash
ENV=production uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=services --cov=routes --cov-report=html

# Run specific test file
pytest tests/test_user_service.py -v
```

## Security Considerations

1. **JWT Secret**: Must be set via environment variable, never hardcoded
2. **Password Hashing**: Uses bcrypt with automatic salt generation
3. **Password Verification**: Old password required for password changes
4. **Input Validation**: All inputs validated via Pydantic models
5. **SQL Injection**: Protected by parameterized queries
6. **CORS**: Configure `allow_origins` appropriately for production

## Error Handling

- **400 Bad Request**: Invalid input data (validation errors)
- **401 Unauthorized**: Invalid/expired JWT token or incorrect password
- **404 Not Found**: User not found
- **500 Internal Server Error**: Database or unexpected errors

All errors return JSON:
```json
{
  "detail": "Error message"
}
```

## Logging

- All operations logged at INFO level
- Errors logged with full traceback
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Database Migrations

For schema changes:

1. Backup existing database: `cp app.db app.db.backup`
2. Modify `init_database()` in `main.py`
3. Add migration logic if needed (e.g., ALTER TABLE)
4. Test with test database first

## Performance Notes

- SQLite `busy_timeout` set to 5000ms for concurrent writes
- Async operations prevent blocking event loop
- Database connection pooling via context managers
- Index on `username` for faster lookups

## Future Enhancements

- [ ] Email verification for email changes
- [ ] Rate limiting on password change attempts
- [ ] Avatar upload to cloud storage
- [ ] Audit log for sensitive operations
- [ ] Multi-factor authentication support