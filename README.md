# User Information Update API

A complete user management system with profile update, password change, and preferences storage capabilities.

## Features

- **User Authentication**: Register and login with JWT token-based authentication
- **Profile Management**: Update nickname and avatar URL
- **Password Change**: Secure password update with current password verification
- **Preferences Storage**: Store and retrieve user preferences as JSON
- **Persistent Storage**: SQLite database with async operations

## Tech Stack

### Backend
- **FastAPI**: Modern async web framework
- **SQLite**: Lightweight database with aiosqlite for async operations
- **bcrypt**: Secure password hashing
- **JWT**: Token-based authentication
- **Pydantic v2**: Data validation and serialization

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Single HTML file**: All CSS and JS inlined for easy deployment
- **Responsive Design**: Mobile-friendly interface

## Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The API will start on `http://localhost:8080`

### Frontend Setup

Simply open `frontend/index.html` in a web browser. The frontend will connect to the backend API automatically.

## API Endpoints

### Authentication

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure123"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "nickname": null,
    "avatar_url": null,
    "preferences": {},
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### User Management (Requires Authentication)

All endpoints below require `Authorization: Bearer <token>` header.

#### Get Current User
```http
GET /api/users/me
Authorization: Bearer <token>
```

#### Update Profile
```http
PATCH /api/users/me/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "nickname": "John",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

#### Change Password
```http
PATCH /api/users/me/password
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "secure123",
  "new_password": "newsecure456"
}
```

#### Update Preferences
```http
PATCH /api/users/me/preferences
Authorization: Bearer <token>
Content-Type: application/json

{
  "preferences": {
    "theme": "dark",
    "language": "en",
    "notifications": true
  }
}
```

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nickname TEXT,
    avatar_url TEXT,
    preferences TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Security Features

- **Password Hashing**: bcrypt with automatic salt generation
- **JWT Tokens**: 24-hour expiration, secure secret key
- **Input Validation**: Pydantic models with strict validation rules
- **SQL Injection Prevention**: Parameterized queries with aiosqlite
- **CORS**: Configured for cross-origin requests

## Environment Variables

```bash
# Optional: Override default port
PORT=8080

# Required in production: Set secure JWT secret
JWT_SECRET=your-secret-key-change-in-production
```

## Development

### Run with Auto-reload
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Testing

You can test the API using curl:

```bash
# Register
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123"}'

# Login and save token
TOKEN=$(curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}' | jq -r '.access_token')

# Update profile
curl -X PATCH http://localhost:8080/api/users/me/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nickname":"Test User","avatar_url":"https://via.placeholder.com/150"}'
```

## Production Deployment

1. **Set secure JWT secret**:
   ```bash
   export JWT_SECRET=$(openssl rand -hex 32)
   ```

2. **Use production ASGI server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
   ```

3. **Enable HTTPS**: Use reverse proxy (nginx/Caddy) with SSL certificate

4. **Database**: Consider migrating to PostgreSQL for production workloads

## License

MIT
