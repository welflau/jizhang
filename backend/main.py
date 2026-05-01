import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import aiosqlite
import bcrypt
import jwt

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="User Management API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

DB_PATH = "app.db"


# Database initialization
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nickname TEXT,
                avatar_url TEXT,
                preferences TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


@app.on_event("startup")
async def startup():
    await init_db()
    logger.info("Database initialized")


# Dependency: Database connection
async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


# Dependency: Current user from JWT
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = await cursor.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return dict(user)


# Schemas
class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    email: str = Field(pattern=r".+@.+\..+")
    password: str = Field(min_length=6, max_length=100)


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)
    preferences: Optional[dict] = None

    @validator("avatar_url")
    def validate_avatar_url(cls, v):
        if v and not (v.startswith("http://") or v.startswith("https://") or v.startswith("data:image/")):
            raise ValueError("Invalid avatar URL format")
        return v


class PasswordUpdateRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=100)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: Optional[str]
    avatar_url: Optional[str]
    preferences: dict
    created_at: str
    updated_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {"user_id": user_id, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def format_user_response(user: dict) -> dict:
    import json
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "nickname": user["nickname"],
        "avatar_url": user["avatar_url"],
        "preferences": json.loads(user["preferences"]) if user["preferences"] else {},
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
    }


# Routes
@app.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest, db=Depends(get_db)):
    # Check if username or email exists
    cursor = await db.execute("SELECT id FROM users WHERE username = ? OR email = ?", (req.username, req.email))
    existing = await cursor.fetchone()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")

    password_hash = hash_password(req.password)
    cursor = await db.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (req.username, req.email, password_hash),
    )
    await db.commit()
    user_id = cursor.lastrowid

    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = await cursor.fetchone()
    token = create_access_token(user_id)

    return {"access_token": token, "token_type": "bearer", "user": format_user_response(dict(user))}


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: UserLoginRequest, db=Depends(get_db)):
    cursor = await db.execute("SELECT * FROM users WHERE username = ?", (req.username,))
    user = await cursor.fetchone()
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user["id"])
    return {"access_token": token, "token_type": "bearer", "user": format_user_response(dict(user))}


@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return format_user_response(current_user)


@app.patch("/api/users/me", response_model=UserResponse)
async def update_user_info(req: UserUpdateRequest, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    import json

    update_fields = []
    params = []

    if req.nickname is not None:
        update_fields.append("nickname = ?")
        params.append(req.nickname)

    if req.avatar_url is not None:
        update_fields.append("avatar_url = ?")
        params.append(req.avatar_url)

    if req.preferences is not None:
        update_fields.append("preferences = ?")
        params.append(json.dumps(req.preferences))

    if not update_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(current_user["id"])

    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
    await db.execute(query, params)
    await db.commit()

    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (current_user["id"],))
    updated_user = await cursor.fetchone()

    logger.info(f"User {current_user['username']} updated profile")
    return format_user_response(dict(updated_user))


@app.put("/api/users/me/password")
async def update_password(req: PasswordUpdateRequest, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    if not verify_password(req.old_password, current_user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")

    new_hash = hash_password(req.new_password)
    await db.execute(
        "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_hash, current_user["id"]),
    )
    await db.commit()

    logger.info(f"User {current_user['username']} changed password")
    return {"message": "Password updated successfully"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled exception: %s", exc)
    return {"error": "Internal server error"}


if __name__ == "__main__":
    import uvicorn

    PORT = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
