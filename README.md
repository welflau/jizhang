# User Information Update API

## Features

Complete user profile management system with:

- **Nickname Update**: Change display name (1-100 characters)
- **Avatar Management**: Update profile picture URL
- **Password Change**: Secure password update with current password verification
  - Minimum 6 characters
  - Must contain at least one letter and one number
  - Encrypted with bcrypt
- **Preferences Storage**: Persist user settings as JSON
  - Automatic merge with existing preferences
  - Supports any JSON-serializable data

## API Endpoints

### Update User Information

```http
PUT /api/users/me
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "nickname": "New Nickname",
  "avatar_url": "https://example.com/avatar.jpg",
  "current_password": "OldPass123",
  "new_password": "NewPass456",
  "preferences": {
    "theme": "dark",
    "language": "en",
    "notifications": true
  }
}
```

**Response:**

```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "nickname": "New Nickname",
  "avatar_url": "https://example.com/avatar.jpg",
  "preferences": {
    "theme": "dark",
    "language": "en",
    "notifications": true
  },
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-02T12:30:00"
}
```

### Get Current User

```http
GET /api/users/me
Authorization: Bearer <jwt_token>
```

## Security

- **Authentication Required**: All endpoints require valid JWT token
- **Authorization**: Users can only update their own information
- **Password Verification**: Current password must be provided when changing password
- **Password Encryption**: All passwords hashed with bcrypt (cost factor 12)
- **Input Validation**: Pydantic schemas validate all input data

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),
    preferences TEXT,  -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export JWT_SECRET_KEY="your-secret-key-change-in-production"
export DATABASE_URL="sqlite+aiosqlite:///./app.db"

# Run server
python backend/main.py
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

## Architecture

- **Controller Layer** (`user_controller.py`): HTTP request handling and response formatting
- **Service Layer** (`user_service.py`): Business logic and data validation
- **Model Layer** (`user.py`): SQLAlchemy ORM models
- **Schema Layer** (`user.py` in schemas): Pydantic request/response validation
- **Middleware** (`auth.py`): JWT authentication and authorization

## Error Handling

- `400 Bad Request`: Validation error or incorrect current password
- `401 Unauthorized`: Missing or invalid JWT token
- `404 Not Found`: User not found
- `500 Internal Server Error`: Unexpected server error (logged with full traceback)

## Validation Rules

### Nickname
- Length: 1-100 characters
- Cannot be empty or whitespace only
- Automatically trimmed

### Avatar URL
- Must start with `http://`, `https://`, or `/`
- Max length: 500 characters

### Password
- Minimum 6 characters
- Maximum 128 characters
- Must contain at least one letter
- Must contain at least one number

### Preferences
- Must be valid JSON object
- Automatically merged with existing preferences
- No size limit (reasonable use expected)

## Notes

- All fields in update request are optional
- Unchanged fields are preserved
- Preferences are merged (not replaced) with existing values
- Password change requires `current_password` for security
- All timestamps in ISO 8601 format
- Database uses async SQLAlchemy with aiosqlite