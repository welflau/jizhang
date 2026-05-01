# User Authentication System

A full-stack user authentication system with JWT tokens, built with FastAPI (backend) and React (frontend).

## Features

- ✅ User registration with email validation
- ✅ Secure login with JWT tokens (access + refresh)
- ✅ Password hashing with bcrypt
- ✅ Remember me functionality
- ✅ Password reset flow
- ✅ Logout functionality
- ✅ Responsive UI

## Tech Stack

**Backend:**
- FastAPI (async Python web framework)
- SQLAlchemy (async ORM)
- SQLite (database)
- Pydantic v2 (data validation)
- python-jose (JWT)
- passlib + bcrypt (password hashing)

**Frontend:**
- React 18 (via CDN)
- Vanilla CSS
- Single HTML file (no build step)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and set your JWT secret:

```bash
cp .env.example .env
```

Generate a secure secret key:

```bash
openssl rand -hex 32
```

Paste the output into `.env` as `JWT_SECRET_KEY`.

### 3. Run Backend

```bash
python backend/app/main.py
```

Backend will start at `http://localhost:8000`

### 4. Open Frontend

Open `frontend/index.html` in your browser, or serve it:

```bash
python -m http.server 3000 --directory frontend
```

Then visit `http://localhost:3000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get tokens |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Logout (client-side) |
| POST | `/api/auth/password-reset` | Request password reset |

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

## Security Notes

- **Never commit `.env` file** (already in `.gitignore`)
- Use strong JWT secret in production (min 32 chars)
- HTTPS required in production
- Consider adding rate limiting for auth endpoints
- Implement token blacklist for logout in production
- Add email verification for registration

## Project Structure

```
.
├── backend/
│   └── app/
│       ├── main.py              # FastAPI app entry
│       ├── core/
│       │   ├── config.py        # Settings management
│       │   ├── database.py      # DB connection
│       │   └── security.py      # Password & JWT utils
│       ├── models/
│       │   └── user.py          # User SQLAlchemy model
│       ├── routers/
│       │   └── auth.py          # Auth endpoints
│       └── schemas/
│           └── auth.py          # Pydantic schemas
├── frontend/
│   └── index.html               # Single-file React app
├── tests/
│   ├── test_auth_register.py
│   └── test_auth_login.py
├── requirements.txt
├── .env.example
└── README.md
```

## License

MIT