# User Authentication System

JWT-based user registration and login system with FastAPI backend and vanilla JavaScript frontend.

## Features

- ✅ User registration with email or phone number
- ✅ Password validation (min 8 chars, letters + numbers)
- ✅ Secure password hashing with bcrypt
- ✅ JWT token authentication
- ✅ Login with email or phone
- ✅ Token expiration handling
- ✅ Logout functionality
- ✅ Responsive UI design

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI
- SQLite (async with aiosqlite)
- bcrypt for password hashing
- PyJWT for token generation
- Pydantic v2 for validation

**Frontend:**
- Vanilla JavaScript (no build tools)
- Single-file HTML with inline CSS/JS
- LocalStorage for token persistence

## Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
# Edit .env and set JWT_SECRET_KEY (use: openssl rand -hex 32)
```

### 3. Run Backend

```bash
python -m app.main
# Server starts at http://localhost:8080
```

### 4. Run Frontend

Open `frontend/index.html` in your browser, or serve with:

```bash
cd frontend
python -m http.server 3000
# Visit http://localhost:3000
```

## Testing

```bash
cd backend
pytest tests/ -v
```

**Test Coverage:**
- ✅ User registration (email/phone)
- ✅ Duplicate user detection
- ✅ Password validation
- ✅ Login authentication
- ✅ Invalid credentials handling

## API Endpoints

### POST `/api/auth/register`
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",  // optional if phone provided
  "phone": "13800138000",        // optional if email provided
  "password": "SecurePass123"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "phone": "13800138000",
  "created_at": "2024-01-01T00:00:00",
  "is_active": true
}
```

### POST `/api/auth/login`
Authenticate and get JWT token.

**Request:**
```json
{
  "identifier": "user@example.com",  // email or phone
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### POST `/api/auth/logout`
Logout (client-side token removal).

**Response (200):**
```json
{
  "message": "logged out successfully"
}
```

## Security Features

- ✅ Passwords hashed with bcrypt (12 rounds)
- ✅ JWT tokens with expiration
- ✅ No sensitive data in responses
- ✅ Environment variables for secrets
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (parameterized queries)

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── database.py          # DB connection & init
│   │   ├── models/
│   │   │   └── user.py          # Pydantic schemas
│   │   ├── routers/
│   │   │   └── auth.py          # Auth endpoints
│   │   └── utils/
│   │       ├── password.py      # bcrypt helpers
│   │       └── jwt_handler.py   # JWT creation/validation
│   ├── tests/
│   │   ├── test_auth_register.py
│   │   └── test_auth_login.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
├── frontend/
│   └── index.html               # Single-file UI
└── README.md
```

## Configuration

**Environment Variables (.env):**

| Variable | Default | Description |
|----------|---------|-------------|
| JWT_SECRET_KEY | (required) | Secret key for JWT signing |
| JWT_EXPIRE_MINUTES | 1440 | Token expiration (24 hours) |
| DATABASE_PATH | app.db | SQLite database file path |
| PORT | 8080 | Backend server port |

## Development Notes

- All backend routes use `async def` for consistency
- Database uses aiosqlite for async operations
- Frontend stores JWT in localStorage (consider httpOnly cookies for production)
- CORS enabled for all origins (restrict in production)
- SQLite busy_timeout set to 5000ms for concurrent writes

## Production Checklist

- [ ] Change JWT_SECRET_KEY to strong random value
- [ ] Set specific CORS origins
- [ ] Use HTTPS for all requests
- [ ] Implement rate limiting
- [ ] Add refresh token mechanism
- [ ] Use httpOnly cookies instead of localStorage
- [ ] Set up proper logging
- [ ] Add monitoring/alerting
- [ ] Database backups
- [ ] Consider PostgreSQL for production

## License

MIT
