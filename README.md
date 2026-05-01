# User Management System

A full-stack user management system with authentication, profile management, and preferences storage.

## Features

- **User Authentication**
  - Register new accounts with username, email, and password
  - Login with username or email
  - JWT token-based authentication
  - Secure password hashing with bcrypt

- **Profile Management**
  - Update nickname and avatar URL
  - Change password (requires current password verification)
  - Store custom user preferences as JSON
  - View complete user information

- **Security**
  - Password hashing with bcrypt
  - JWT token expiration (24 hours)
  - Current password verification for password changes
  - CORS enabled for frontend-backend communication

## Tech Stack

### Backend
- **FastAPI**: Modern async web framework
- **SQLite**: Lightweight database with aiosqlite for async operations
- **Pydantic v2**: Data validation and serialization
- **bcrypt**: Password hashing
- **PyJWT**: JSON Web Token implementation

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Single HTML file**: All CSS and JS inlined
- **Responsive design**: Mobile-friendly interface

## Installation

### Backend Setup

1. Install Python 3.11 or higher

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8080`

### Frontend Setup

1. Open `frontend/index.html` in a web browser
2. The frontend will connect to the backend at `http://localhost:8080/api`

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
  ```json
  {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password"
  }
  ```

- `POST /api/auth/login` - Login user
  ```json
  {
    "username": "john_doe",
    "password": "secure_password"
  }
  ```

### User Management

- `GET /api/users/me` - Get current user info (requires authentication)

- `PUT /api/users/me` - Update user information (requires authentication)
  ```json
  {
    "nickname": "John",
    "avatar_url": "https://example.com/avatar.jpg",
    "current_password": "old_password",
    "new_password": "new_password",
    "preferences": {
      "theme": "dark",
      "language": "en"
    }
  }
  ```

- `DELETE /api/users/me` - Delete user account (requires authentication)

### Health Check

- `GET /health` - Server health status

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nickname TEXT,
    avatar_url TEXT,
    preferences TEXT,  -- JSON string
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

## Environment Variables

- `JWT_SECRET_KEY`: Secret key for JWT token signing (default: "your-secret-key-change-in-production")
- `PORT`: Server port (default: 8080)

**Important**: Change `JWT_SECRET_KEY` in production!

## Security Considerations

1. **Password Storage**: Passwords are hashed using bcrypt before storage
2. **Token Expiration**: JWT tokens expire after 24 hours
3. **Password Change**: Requires current password verification
4. **CORS**: Configured for development (allow all origins). Restrict in production!
5. **Secret Key**: Use environment variable for JWT secret in production

## Development

### Running in Development Mode

Backend with auto-reload:
```bash
cd backend
python main.py
```

The server will automatically reload on code changes.

### Testing

1. Register a new account
2. Login with credentials
3. Update profile information
4. Change password
5. Save custom preferences
6. Logout and login again to verify persistence

## Production Deployment

1. Set `JWT_SECRET_KEY` environment variable to a strong random string
2. Configure CORS to allow only your frontend domain
3. Use a production WSGI server (e.g., gunicorn with uvicorn workers)
4. Consider using PostgreSQL instead of SQLite for better concurrency
5. Enable HTTPS
6. Set up proper logging and monitoring

## License

MIT License
