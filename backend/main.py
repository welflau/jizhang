import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
import aiosqlite
import bcrypt
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
DB_PATH = "app.db"

app = FastAPI(title="User Authentication API")
security = HTTPBearer()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, max_length=100, description="Password (min 8 chars)")
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$", description="Phone number (E.164 format)")

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=100)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    phone: Optional[str]
    created_at: str

class MessageResponse(BaseModel):
    message: str

# Database initialization
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                used BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
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

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db = Depends(get_db)):
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = await cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return dict(user)

# API endpoints
@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest, db = Depends(get_db)):
    """Register a new user with email and password"""
    # Check if user already exists
    cursor = await db.execute("SELECT id FROM users WHERE email = ?", (req.email,))
    existing = await cursor.fetchone()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Hash password and create user
    password_hash = hash_password(req.password)
    
    try:
        cursor = await db.execute(
            "INSERT INTO users (email, phone, password_hash) VALUES (?, ?, ?)",
            (req.email, req.phone, password_hash)
        )
        await db.commit()
        user_id = cursor.lastrowid
        
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = await cursor.fetchone()
        
        logger.info(f"User registered: {req.email}")
        return UserResponse(
            id=user["id"],
            email=user["email"],
            phone=user["phone"],
            created_at=user["created_at"]
        )
    except Exception as e:
        logger.exception(f"Registration error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: UserLoginRequest, db = Depends(get_db)):
    """Login with email and password, returns JWT tokens"""
    cursor = await db.execute("SELECT * FROM users WHERE email = ?", (req.email,))
    user = await cursor.fetchone()
    
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    
    # Create tokens
    token_data = {"sub": str(user["id"]), "email": user["email"]}
    
    if req.remember_me:
        access_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(token_data, access_token_expires)
    refresh_token = create_refresh_token(token_data)
    
    logger.info(f"User logged in: {req.email}")
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@app.post("/api/auth/refresh", response_model=TokenResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh access token using refresh token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    
    token_data = {"sub": payload["sub"], "email": payload["email"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@app.post("/api/auth/logout", response_model=MessageResponse)
async def logout(user = Depends(get_current_user)):
    """Logout current user (client should discard tokens)"""
    logger.info(f"User logged out: {user['email']}")
    return MessageResponse(message="Logged out successfully")

@app.post("/api/auth/password-reset", response_model=MessageResponse)
async def request_password_reset(req: PasswordResetRequest, db = Depends(get_db)):
    """Request password reset token (sent via email in production)"""
    cursor = await db.execute("SELECT id FROM users WHERE email = ?", (req.email,))
    user = await cursor.fetchone()
    
    if not user:
        # Don't reveal if email exists
        return MessageResponse(message="If email exists, reset link has been sent")
    
    # Generate reset token
    reset_token_data = {"sub": str(user["id"]), "email": req.email, "type": "reset"}
    reset_token = jwt.encode(reset_token_data, SECRET_KEY, algorithm=ALGORITHM)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    await db.execute(
        "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
        (user["id"], reset_token, expires_at.isoformat())
    )
    await db.commit()
    
    # In production: send email with reset link
    logger.info(f"Password reset requested for: {req.email}, token: {reset_token}")
    return MessageResponse(message="If email exists, reset link has been sent")

@app.post("/api/auth/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(req: PasswordResetConfirm, db = Depends(get_db)):
    """Reset password using token"""
    # Verify token
    try:
        payload = jwt.decode(req.token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "reset":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    
    # Check if token exists and not used
    cursor = await db.execute(
        "SELECT * FROM password_reset_tokens WHERE token = ? AND used = 0 AND expires_at > ?",
        (req.token, datetime.utcnow().isoformat())
    )
    token_record = await cursor.fetchone()
    
    if not token_record:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    
    # Update password
    user_id = token_record["user_id"]
    new_password_hash = hash_password(req.new_password)
    
    await db.execute(
        "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_password_hash, user_id)
    )
    await db.execute(
        "UPDATE password_reset_tokens SET used = 1 WHERE id = ?",
        (token_record["id"],)
    )
    await db.commit()
    
    logger.info(f"Password reset completed for user_id: {user_id}")
    return MessageResponse(message="Password reset successfully")

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(user = Depends(get_current_user)):
    """Get current authenticated user information"""
    return UserResponse(
        id=user["id"],
        email=user["email"],
        phone=user["phone"],
        created_at=user["created_at"]
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception(f"Unhandled exception: {exc}")
    return {"error": "Internal server error"}, 500

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
