# User Profile Update API

## Overview

FastAPI-based backend service for user profile management with JWT authentication.

## Features

- ✅ JWT authentication middleware
- ✅ User profile retrieval (GET /api/user/profile)
- ✅ User profile update (PATCH /api/user/profile)
  - Nickname update
  - Avatar URL update (with validation)
  - Password change (with current password verification)
  - User preferences (theme, language, notifications)
- ✅ Password security (bcrypt hashing with salt rounds=10)
- ✅ Input validation (Pydantic v2 schemas)
- ✅ Comprehensive test coverage

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: SQLite (async via aiosqlite)
- **Authentication**: JWT (PyJWT)
- **Password Hashing**: bcrypt
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio

## Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── models/
│   └── user.py            # Pydantic schemas
├── services/
│   └── user_service.py    # Database operations
├── routes/
│   └── user_routes.py     # API endpoints
├── middleware/
│   └── auth.py            # JWT authentication
├── tests/
│   └── test_user_routes.py # Unit tests
├── init_db.py             # Database initialization
└── requirements.txt       # Python dependencies
```

## Setup

### 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Initialize Database

```bash
python backend/init_db.py
```

This creates `app.db` with the `users` table.

### 3. Set Environment Variables

```bash
export JWT_SECRET="your-secret-key-change-in-production"
export PORT=8080
```

### 4. Run Server

```bash
python backend/main.py
```

Or with uvicorn directly:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload
```

## API Endpoints

### GET /api/user/profile

Get current user profile.

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Response** (200):
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "nickname": "JohnDoe",
  "avatar": "https://example.com/avatar.jpg",
  "preferences": {
    "theme": "dark",
    "language": "en",
    "notifications_enabled": true
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z"
}
```

### PATCH /api/user/profile

Update current user profile.

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Request Body** (all fields optional):
```json
{
  "nickname": "NewNickname",
  "avatar": "https://example.com/new-avatar.jpg",
  "current_password": "OldPass123",
  "new_password": "NewPass456",
  "preferences": {
    "theme": "dark",
    "language": "zh",
    "notifications_enabled": false,
    "email_notifications": true
  }
}
```

**Validation Rules**:
- `nickname`: 2-50 characters
- `avatar`: Valid HTTP/HTTPS URL
- `new_password`: Min 8 chars, must contain uppercase, lowercase, and digit
- `current_password`: Required when changing password

**Response** (200):
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "nickname": "NewNickname",
  "avatar": "https://example.com/new-avatar.jpg",
  "preferences": {"theme": "dark", "language": "zh"},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T10:30:00Z"
}
```

**Error Responses**:
- `400`: Invalid request data (e.g., missing current_password when changing password)
- `401`: Invalid/expired token or incorrect current password
- `404`: User not found
- `422`: Validation error (weak password, invalid URL, etc.)

## Testing

Run all tests:

```bash
pytest backend/tests/ -v
```

Run specific test:

```bash
pytest backend/tests/test_user_routes.py::test_update_profile_password_success -v
```

**Test Coverage**:
- ✅ GET profile with valid token
- ✅ GET profile unauthorized (no token)
- ✅ GET profile with invalid token
- ✅ PATCH update nickname
- ✅ PATCH update avatar (valid URL)
- ✅ PATCH update avatar (invalid URL)
- ✅ PATCH change password (correct current password)
- ✅ PATCH change password (wrong current password)
- ✅ PATCH change password (missing current password)
- ✅ PATCH weak password validation
- ✅ PATCH update preferences
- ✅ PATCH update multiple fields at once

## Security Features

1. **Password Hashing**: bcrypt with 10 salt rounds
2. **JWT Authentication**: 7-day token expiration
3. **Input Validation**: Pydantic schemas with regex patterns
4. **SQL Injection Prevention**: Parameterized queries via aiosqlite
5. **Sensitive Data Protection**: Password hash never exposed in API responses
6. **CORS**: Configurable origin whitelist (currently allows all for development)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | `your-secret-key-change-in-production` | JWT signing secret |
| `PORT` | `8080` | Server port |

⚠️ **Production Checklist**:
- [ ] Change `JWT_SECRET` to a strong random value
- [ ] Configure CORS `allow_origins` to specific domains
- [ ] Use HTTPS in production
- [ ] Set up proper logging and monitoring
- [ ] Use environment-specific `.env` files (never commit secrets)

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nickname TEXT,
    avatar TEXT,
    preferences TEXT DEFAULT '{}',  -- JSON string
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

## Troubleshooting

### Database Locked Error

If you see `database is locked` errors:

```python
# In user_service.py, increase timeout:
async with aiosqlite.connect(self.db_path, timeout=10.0) as db:
    ...
```

### Token Expired

Generate a new token using `AuthMiddleware.create_token(user_id, username)`.

### Test Database Conflicts

Tests use `test_app.db`. If tests fail, manually delete it:

```bash
rm test_app.db
```

## License

MIT