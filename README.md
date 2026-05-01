# User Authentication System

A complete user authentication system with registration, login, password reset, and JWT token-based authentication.

## Features

- ✅ User registration with email and optional phone
- ✅ Secure password hashing with bcrypt
- ✅ Login with "Remember Me" option
- ✅ JWT access and refresh tokens
- ✅ Password reset flow with token validation
- ✅ Protected user profile endpoint
- ✅ Logout functionality
- ✅ Responsive React frontend (single HTML file)
- ✅ FastAPI async backend
- ✅ SQLite database with async support

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI (async web framework)
- aiosqlite (async SQLite)
- bcrypt (password hashing)
- PyJWT (JWT tokens)
- Pydantic v2 (data validation)

**Frontend:**
- React 18 (via CDN)
- Vanilla CSS
- Single HTML file (no build process)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and change JWT_SECRET_KEY to a secure random string
```

### 3. Run Backend

```bash
python main.py
```

Backend will start at `http://localhost:8080`

### 4. Open Frontend

Open `frontend/index.html` in your browser or serve it:

```bash
cd frontend
python -m http.server 3000
```

Then visit `http://localhost:3000`

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Logout (invalidate tokens) |
| GET | `/api/auth/me` | Get current user info |

### Password Reset

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/password-reset` | Request reset token |
| POST | `/api/auth/password-reset/confirm` | Reset password with token |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server health status |

## Usage Examples

### Register User

```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "phone": "+1234567890"
  }'
```

### Login

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "remember_me": true
  }'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Get User Info

```bash
curl http://localhost:8080/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Password Reset Flow

1. Request reset token:
```bash
curl -X POST http://localhost:8080/api/auth/password-reset \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

2. Check server logs for token (in production, this would be sent via email)

3. Reset password:
```bash
curl -X POST http://localhost:8080/api/auth/password-reset/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "token": "RESET_TOKEN_FROM_LOGS",
    "new_password": "NewSecurePass456"
  }'
```

## Security Features

- ✅ Passwords hashed with bcrypt (salt rounds: 12)
- ✅ JWT tokens with expiration
- ✅ Refresh token rotation
- ✅ Password reset tokens expire in 1 hour
- ✅ One-time use reset tokens
- ✅ No sensitive data in logs
- ✅ Environment variables for secrets
- ✅ CORS configured
- ✅ Input validation with Pydantic

## Database Schema

### users table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### password_reset_tokens table
```sql
CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Frontend Features

- ✅ Responsive design (mobile-friendly)
- ✅ Form validation
- ✅ Error handling with user-friendly messages
- ✅ Loading states
- ✅ Token storage in localStorage
- ✅ Automatic token refresh
- ✅ Protected routes
- ✅ Clean UI with gradient background

## Production Deployment

### Environment Variables

**Required:**
- `JWT_SECRET_KEY` - Strong random string (use `openssl rand -hex 32`)

**Optional:**
- `PORT` - Server port (default: 8080)
- `DATABASE_PATH` - SQLite database path (default: app.db)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Access token lifetime (default: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token lifetime (default: 7)

### Production Checklist

- [ ] Change `JWT_SECRET_KEY` to a secure random value
- [ ] Set up HTTPS/TLS
- [ ] Configure CORS for your domain only
- [ ] Set up email service for password reset
- [ ] Use PostgreSQL instead of SQLite for production
- [ ] Set up logging to file/service
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerts
- [ ] Regular database backups
- [ ] Use environment-specific `.env` files

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
EXPOSE 8080
CMD ["python", "main.py"]
```

## Development

### Run with Auto-reload

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Testing

Test endpoints with the included frontend or use tools like:
- curl
- Postman
- HTTPie
- FastAPI auto-generated docs at `http://localhost:8080/docs`

## Troubleshooting

### Database locked error
- Increase `busy_timeout` in database connection
- Use connection pooling
- Consider PostgreSQL for high concurrency

### Token expired
- Frontend automatically refreshes tokens
- Check token expiration settings in `.env`

### CORS errors
- Update `allow_origins` in `main.py` for your domain
- In development, `*` is used (not secure for production)

## License

MIT License - feel free to use in your projects.

## Support

For issues or questions, check:
- FastAPI docs: https://fastapi.tiangolo.com
- React docs: https://react.dev
- JWT docs: https://jwt.io
