# User Profile Management System

## Overview

A full-stack user management system with profile update capabilities, built with FastAPI backend and vanilla JavaScript frontend.

## Features

- **User Authentication**: Register and login with JWT tokens
- **Profile Management**: Update nickname, avatar, and preferences
- **Password Change**: Secure password update with old password verification
- **Persistent Storage**: SQLite database with async operations
- **Responsive UI**: Mobile-friendly single-page application

## Tech Stack

### Backend
- FastAPI (async web framework)
- SQLite with aiosqlite (async database)
- JWT authentication
- bcrypt password hashing
- Pydantic v2 validation

### Frontend
- Vanilla JavaScript (no build tools)
- Single HTML file with inline CSS/JS
- Fetch API for HTTP requests
- LocalStorage for token persistence

## Installation

### Prerequisites
- Python 3.11+
- pip

### Setup

1. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Start the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8080`

3. Open the frontend:
```bash
cd frontend
# Open index.html in your browser or use a local server:
python -m http.server 3000
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### User Management
- `GET /api/users/me` - Get current user profile
- `PATCH /api/users/me` - Update profile (nickname, avatar, preferences)
- `PUT /api/users/me/password` - Change password

## Security Features

- JWT token-based authentication
- bcrypt password hashing
- Password strength validation (min 6 characters)
- Old password verification for password changes
- CORS enabled for development
- Environment variable support for secrets

## Configuration

Environment variables:
- `JWT_SECRET` - Secret key for JWT signing (default: dev-secret-change-in-production)
- `PORT` - Backend server port (default: 8080)

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

## Usage Examples

### Register a new user
```javascript
fetch('http://localhost:8080/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_doe',
    email: 'john@example.com',
    password: 'secure123'
  })
});
```

### Update profile
```javascript
fetch('http://localhost:8080/api/users/me', {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  },
  body: JSON.stringify({
    nickname: 'John',
    avatar_url: 'https://example.com/avatar.jpg',
    preferences: { theme: 'dark', language: 'en' }
  })
});
```

## Development Notes

- All async operations use `async/await` pattern
- Database connections use context managers for proper cleanup
- Frontend uses localStorage for token persistence
- No build process required - single HTML file deployment
- Error handling with proper HTTP status codes
- Logging enabled for debugging

## Production Considerations

1. Change `JWT_SECRET` to a strong random value
2. Use environment variables for all secrets
3. Enable HTTPS
4. Configure CORS for specific origins
5. Add rate limiting
6. Use production-grade database (PostgreSQL)
7. Implement refresh tokens
8. Add input sanitization for XSS prevention

## License

MIT
