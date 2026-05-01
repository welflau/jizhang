import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
import aiosqlite
import bcrypt
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="User Management API")

# CORS configuration
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

DB_PATH = "users.db"


# Database initialization
async def init_db():
    """Initialize SQLite database with users table"""
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
async def startup_event():
    await init_db()
    logger.info("Database initialized")


# Dependency: Database connection
async def get_db():
    """Provide async database connection"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


# Dependency: Current user from JWT
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)):
    """Extract and validate current user from JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = await cursor.fetchone()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        return dict(user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# Pydantic models
class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    email: str = Field(pattern=r".+@.+\..+")
    password: str = Field(min_length=6, max_length=100)


class LoginRequest(BaseModel):
    username: str
    password: str


class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = Field(None, min_length=1, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)
    
    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, v):
        if v and not (v.startswith("http://") or v.startswith("https://") or v.startswith("data:image/")):
            raise ValueError("avatar_url must be a valid HTTP(S) URL or data URI")
        return v


class UpdatePasswordRequest(BaseModel):
    current_password: str = Field(min_length=6)
    new_password: str = Field(min_length=6, max_length=100)


class UpdatePreferencesRequest(BaseModel):
    preferences: dict = Field(default_factory=dict)
    
    @field_validator("preferences")
    @classmethod
    def validate_preferences(cls, v):
        # Ensure preferences is a flat dict with string keys
        if not isinstance(v, dict):
            raise ValueError("preferences must be a dictionary")
        for key in v.keys():
            if not isinstance(key, str):
                raise ValueError("preference keys must be strings")
        return v


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
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(user_id: int) -> str:
    """Generate JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


import json

def row_to_user_response(row: dict) -> UserResponse:
    """Convert database row to UserResponse model"""
    preferences = {}
    if row.get("preferences"):
        try:
            preferences = json.loads(row["preferences"])
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in preferences for user {row['id']}")
    
    return UserResponse(
        id=row["id"],
        username=row["username"],
        email=row["email"],
        nickname=row.get("nickname"),
        avatar_url=row.get("avatar_url"),
        preferences=preferences,
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )


# API endpoints
@app.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db=Depends(get_db)):
    """Register new user"""
    # Check if username or email already exists
    cursor = await db.execute("SELECT id FROM users WHERE username = ? OR email = ?", (req.username, req.email))
    existing = await cursor.fetchone()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")
    
    # Create user
    password_hash = hash_password(req.password)
    cursor = await db.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (req.username, req.email, password_hash)
    )
    await db.commit()
    user_id = cursor.lastrowid
    
    # Fetch created user
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = await cursor.fetchone()
    user = row_to_user_response(dict(user_row))
    
    # Generate token
    token = create_access_token(user_id)
    
    return TokenResponse(access_token=token, user=user)


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest, db=Depends(get_db)):
    """User login"""
    cursor = await db.execute("SELECT * FROM users WHERE username = ?", (req.username,))
    user_row = await cursor.fetchone()
    
    if not user_row or not verify_password(req.password, user_row["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    user = row_to_user_response(dict(user_row))
    token = create_access_token(user.id)
    
    return TokenResponse(access_token=token, user=user)


@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return row_to_user_response(current_user)


@app.patch("/api/users/me/profile", response_model=UserResponse)
async def update_profile(req: UpdateProfileRequest, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """Update user profile (nickname and avatar)"""
    update_fields = []
    params = []
    
    if req.nickname is not None:
        update_fields.append("nickname = ?")
        params.append(req.nickname)
    
    if req.avatar_url is not None:
        update_fields.append("avatar_url = ?")
        params.append(req.avatar_url)
    
    if not update_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    params.append(current_user["id"])
    
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
    await db.execute(query, params)
    await db.commit()
    
    # Fetch updated user
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (current_user["id"],))
    updated_user = await cursor.fetchone()
    
    return row_to_user_response(dict(updated_user))


@app.patch("/api/users/me/password")
async def update_password(req: UpdatePasswordRequest, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """Update user password"""
    # Verify current password
    if not verify_password(req.current_password, current_user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    
    # Hash new password
    new_password_hash = hash_password(req.new_password)
    
    # Update password
    await db.execute(
        "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_password_hash, current_user["id"])
    )
    await db.commit()
    
    return {"message": "Password updated successfully"}


@app.patch("/api/users/me/preferences", response_model=UserResponse)
async def update_preferences(req: UpdatePreferencesRequest, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """Update user preferences"""
    preferences_json = json.dumps(req.preferences)
    
    await db.execute(
        "UPDATE users SET preferences = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (preferences_json, current_user["id"])
    )
    await db.commit()
    
    # Fetch updated user
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (current_user["id"],))
    updated_user = await cursor.fetchone()
    
    return row_to_user_response(dict(updated_user))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
