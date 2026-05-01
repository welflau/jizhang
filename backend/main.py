import os
import logging
from datetime import datetime, timedelta
from typing import Optional

import aiosqlite
import bcrypt
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import jwt

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATABASE_PATH = "app.db"
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

app = FastAPI(title="User Management API")
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30, description="Username")
    email: str = Field(pattern=r".+@.+\..+", description="Email address")
    password: str = Field(min_length=6, description="Password")


class UserLoginRequest(BaseModel):
    username: str = Field(description="Username or email")
    password: str = Field(description="Password")


class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50, description="Display nickname")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar image URL")
    current_password: Optional[str] = Field(None, description="Current password for verification")
    new_password: Optional[str] = Field(None, min_length=6, description="New password")
    preferences: Optional[dict] = Field(None, description="User preferences as JSON object")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = None
    created_at: str
    updated_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    message: str


# Database dependency
async def get_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


# Initialize database
async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nickname TEXT,
                avatar_url TEXT,
                preferences TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.commit()
    logger.info("Database initialized")


@app.on_event("startup")
async def startup_event():
    await init_db()


# Auth utilities
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)) -> dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = await cursor.fetchone()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return dict(user)


def row_to_user_response(row: dict) -> UserResponse:
    import json
    preferences = None
    if row.get("preferences"):
        try:
            preferences = json.loads(row["preferences"])
        except json.JSONDecodeError:
            preferences = None
    
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


# API Endpoints
@app.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest, db=Depends(get_db)):
    """Register a new user account"""
    # Check if username or email already exists
    cursor = await db.execute("SELECT id FROM users WHERE username = ? OR email = ?", (req.username, req.email))
    existing = await cursor.fetchone()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")

    # Hash password and create user
    password_hash = hash_password(req.password)
    now = datetime.utcnow().isoformat()
    
    cursor = await db.execute(
        "INSERT INTO users (username, email, password_hash, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (req.username, req.email, password_hash, now, now)
    )
    await db.commit()
    user_id = cursor.lastrowid

    # Fetch created user
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = await cursor.fetchone()
    user_dict = dict(user_row)

    # Generate token
    access_token = create_access_token(data={"sub": user_id})
    
    return TokenResponse(
        access_token=access_token,
        user=row_to_user_response(user_dict)
    )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: UserLoginRequest, db=Depends(get_db)):
    """Login with username/email and password"""
    # Find user by username or email
    cursor = await db.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (req.username, req.username)
    )
    user_row = await cursor.fetchone()
    
    if not user_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    user_dict = dict(user_row)
    
    # Verify password
    if not verify_password(req.password, user_dict["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Generate token
    access_token = create_access_token(data={"sub": user_dict["id"]})
    
    return TokenResponse(
        access_token=access_token,
        user=row_to_user_response(user_dict)
    )


@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return row_to_user_response(current_user)


@app.put("/api/users/me", response_model=UserResponse)
async def update_user_info(req: UserUpdateRequest, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """Update current user information including nickname, avatar, password, and preferences"""
    import json
    
    user_id = current_user["id"]
    update_fields = []
    update_values = []
    
    # Update nickname
    if req.nickname is not None:
        update_fields.append("nickname = ?")
        update_values.append(req.nickname)
    
    # Update avatar URL
    if req.avatar_url is not None:
        update_fields.append("avatar_url = ?")
        update_values.append(req.avatar_url)
    
    # Update password (requires current password verification)
    if req.new_password is not None:
        if req.current_password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password required to change password"
            )
        
        # Verify current password
        if not verify_password(req.current_password, current_user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Hash and update new password
        new_password_hash = hash_password(req.new_password)
        update_fields.append("password_hash = ?")
        update_values.append(new_password_hash)
    
    # Update preferences
    if req.preferences is not None:
        update_fields.append("preferences = ?")
        update_values.append(json.dumps(req.preferences))
    
    # Check if there are any updates
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Add updated_at timestamp
    update_fields.append("updated_at = ?")
    update_values.append(datetime.utcnow().isoformat())
    
    # Build and execute update query
    update_values.append(user_id)
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
    
    await db.execute(query, tuple(update_values))
    await db.commit()
    
    # Fetch updated user
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    updated_user = await cursor.fetchone()
    
    return row_to_user_response(dict(updated_user))


@app.delete("/api/users/me", response_model=MessageResponse)
async def delete_user_account(current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """Delete current user account (soft delete or hard delete)"""
    user_id = current_user["id"]
    
    await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    await db.commit()
    
    return MessageResponse(message="Account deleted successfully")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled exception: %s", exc)
    return {"error": "Internal server error"}, 500


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
