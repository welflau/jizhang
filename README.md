# User Authentication System

A complete user authentication system with registration, login, password reset, and JWT token-based authentication.

## Features

- ✅ User registration (email/phone + password)
- ✅ User login with "remember me" option
- ✅ JWT token authentication
- ✅ Password reset flow (request + confirm)
- ✅ User profile endpoint
- ✅ Logout functionality
- ✅ Bcrypt password hashing
- ✅ SQLite async database
- ✅ React frontend (single-file HTML)

## Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- aiosqlite (async SQLite)
- bcrypt (password hashing)
- PyJWT (token generation)
- Pydantic v2 (validation)

**Frontend:**
- React 18 (via CDN)
- Vanilla CSS
- Single-file deployment (index.html)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set JWT_SECRET to a secure random string
```

### 3. Run Backend

```bash
python main.py
```

API will be available at `http://localhost:8080`

### 4. Open Frontend

Open `frontend/index.html` in your browser, or serve it:

```bash
cd frontend
python -m http.server 3000
```

Then visit `http://localhost:3000`

## API Endpoints

### Health Check
```
GET /health
```

### Authentication

**Register:**
```
POST /api/auth/register
Body: {"email": "user@example.com", "password": "password123", "phone": "+1234567890"}
Response: {"access_token": "...", "token_type": "bearer", "expires_in": 86400}
```

**Login:**
```
POST /api/auth/login
Body: {"email": "user@example.com", "password": "password123", "remember_me": false}
Response: {"access_token": "...", "token_type": "bearer", "expires_in": 86400}
```

**Get Current User:**
```
GET /api/auth/me
Headers: Authorization: Bearer <token>
Response: {"id": 1, "email": "user@example.com", "phone": "+1234567890", "created_at": "..."}
```

**Logout:**
```
POST /api/auth/logout
Headers: Authorization: Bearer <token>
Response: {"message": "Logged out successfully"}
```

**Request Password Reset:**
```
POST /api/auth/reset-password
Body: {"email": "user@example.com"}
Response: {"message": "If email exists, reset instructions have been sent"}
```

**Confirm Password Reset:**
```
POST /api/auth/reset-password/confirm
Body: {"token": "<reset_token>", "new_password": "newpassword123"}
Response: {"message": "Password reset successfully"}
```

## Security Features

- ✅ Passwords hashed with bcrypt (salt rounds: 12)
- ✅ JWT tokens with expiration (24h default, 7 days with remember_me)
- ✅ Password reset tokens expire after 1 hour
- ✅ Email enumeration protection (same response for existing/non-existing emails)
- ✅ CORS enabled for frontend integration
- ✅ Environment variable for JWT secret (never hardcoded)

## Database Schema

**users table:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

**reset_tokens table:**
```sql
CREATE TABLE reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at TEXT NOT NULL,
    used BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Testing

### Manual Testing

1. Open frontend in browser
2. Register a new user
3. Verify token is stored in localStorage
4. Logout and login again
5. Test "remember me" checkbox
6. Request password reset (check server logs for token)
7. Confirm password reset with token

### API Testing with curl

```bash
# Health check
curl http://localhost:8080/health

# Register
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get user info (replace <token>)
curl http://localhost:8080/api/auth/me \
  -H "Authorization: Bearer <token>"
```

## Production Deployment

1. **Set secure JWT_SECRET:**
   ```bash
   openssl rand -hex 32
   ```

2. **Use production ASGI server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
   ```

3. **Enable HTTPS** (use nginx/caddy as reverse proxy)

4. **Set CORS origins** to your frontend domain (not `*`)

5. **Use PostgreSQL** instead of SQLite for production

6. **Implement email sending** for password reset (currently logs to console)

## License

MIT
