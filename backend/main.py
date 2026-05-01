import os
import logging
import json
import shutil
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, EmailStr
import aiosqlite
import bcrypt

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
DB_PATH = os.getenv("DB_PATH", "app.db")
PORT = int(os.getenv("PORT", "8080"))
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")

app = FastAPI(title="User Auth API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


# Pydantic models
class RegisterRequest(BaseModel):
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, max_length=100, description="Password (min 8 chars)")
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$", description="Optional phone number")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: int
    email: str
    phone: Optional[str]
    created_at: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ConfirmResetRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=100)


class MessageResponse(BaseModel):
    message: str


class BackupResponse(BaseModel):
    filename: str
    created_at: str
    size: int


class RestoreRequest(BaseModel):
    filename: str


# Database dependency
async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


# Initialize database
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                used BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        await db.commit()
    logger.info("Database initialized")


@app.on_event("startup")
async def startup_event():
    await init_db()
    # Create backup directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)


# Utility functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(user_id: int, email: str, remember_me: bool = False) -> tuple[str, int]:
    """Create JWT token"""
    expires_hours = JWT_EXPIRATION_HOURS * 7 if remember_me else JWT_EXPIRATION_HOURS
    expires_delta = timedelta(hours=expires_hours)
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, int(expires_delta.total_seconds())


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db = Depends(get_db)):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = await cursor.fetchone()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# Health check endpoint (verification step)
@app.get("/health", response_model=MessageResponse)
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"message": "ok"}


# Authentication endpoints
@app.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db = Depends(get_db)):
    """Register new user"""
    # Check if email already exists
    cursor = await db.execute("SELECT id FROM users WHERE email = ?", (req.email,))
    existing = await cursor.fetchone()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Hash password
    password_hash = hash_password(req.password)
    
    # Insert user
    now = datetime.utcnow().isoformat()
    cursor = await db.execute(
        "INSERT INTO users (email, phone, password_hash, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (req.email, req.phone, password_hash, now, now)
    )
    await db.commit()
    user_id = cursor.lastrowid
    
    # Generate token
    token, expires_in = create_access_token(user_id, req.email)
    
    logger.info(f"User registered: {req.email}")
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in
    }


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest, db = Depends(get_db)):
    """Login user"""
    # Find user
    cursor = await db.execute("SELECT * FROM users WHERE email = ?", (req.email,))
    user = await cursor.fetchone()
    
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate token
    token, expires_in = create_access_token(user["id"], user["email"], req.remember_me)
    
    logger.info(f"User logged in: {req.email}")
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in
    }


@app.post("/api/auth/logout", response_model=MessageResponse)
async def logout(current_user = Depends(get_current_user)):
    """Logout user (client should discard token)"""
    logger.info(f"User logged out: {current_user['email']}")
    return {"message": "Logged out successfully"}


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "phone": current_user["phone"],
        "created_at": current_user["created_at"]
    }


@app.post("/api/auth/reset-password", response_model=MessageResponse)
async def request_password_reset(req: ResetPasswordRequest, db = Depends(get_db)):
    """Request password reset (generates token)"""
    # Find user
    cursor = await db.execute("SELECT id FROM users WHERE email = ?", (req.email,))
    user = await cursor.fetchone()
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If email exists, reset instructions have been sent"}
    
    # Generate reset token
    import secrets
    reset_token = secrets.token_urlsafe(32)
    expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    
    await db.execute(
        "INSERT INTO reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
        (user["id"], reset_token, expires_at)
    )
    await db.commit()
    
    # In production, send email with reset_token
    logger.info(f"Password reset requested for: {req.email}, token: {reset_token}")
    
    return {"message": "If email exists, reset instructions have been sent"}


@app.post("/api/auth/reset-password/confirm", response_model=MessageResponse)
async def confirm_password_reset(req: ConfirmResetRequest, db = Depends(get_db)):
    """Confirm password reset with token"""
    # Validate token
    cursor = await db.execute(
        "SELECT * FROM reset_tokens WHERE token = ? AND used = 0 AND expires_at > ?",
        (req.token, datetime.utcnow().isoformat())
    )
    reset_record = await cursor.fetchone()
    
    if not reset_record:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    
    # Update password
    password_hash = hash_password(req.new_password)
    now = datetime.utcnow().isoformat()
    
    await db.execute(
        "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
        (password_hash, now, reset_record["user_id"])
    )
    
    # Mark token as used
    await db.execute("UPDATE reset_tokens SET used = 1 WHERE id = ?", (reset_record["id"],))
    await db.commit()
    
    logger.info(f"Password reset confirmed for user_id: {reset_record['user_id']}")
    return {"message": "Password reset successfully"}


# Backup and Restore endpoints
@app.post("/api/backup/create", response_model=BackupResponse)
async def create_backup(current_user = Depends(get_current_user)):
    """Create a backup of the database"""
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.db"
        backup_path = os.path.join(BACKUP_DIR, filename)
        
        # Copy database file
        shutil.copy2(DB_PATH, backup_path)
        
        # Get file size
        file_size = os.path.getsize(backup_path)
        
        logger.info(f"Backup created by user {current_user['email']}: {filename}")
        
        return {
            "filename": filename,
            "created_at": datetime.utcnow().isoformat(),
            "size": file_size
        }
    except Exception as e:
        logger.error(f"Backup creation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Backup creation failed")


@app.get("/api/backup/list", response_model=list[BackupResponse])
async def list_backups(current_user = Depends(get_current_user)):
    """List all available backups"""
    try:
        backups = []
        if os.path.exists(BACKUP_DIR):
            for filename in os.listdir(BACKUP_DIR):
                if filename.endswith('.db'):
                    filepath = os.path.join(BACKUP_DIR, filename)
                    stat = os.stat(filepath)
                    backups.append({
                        "filename": filename,
                        "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "size": stat.st_size
                    })
        
        # Sort by creation time, newest first
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        
        return backups
    except Exception as e:
        logger.error(f"Failed to list backups: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list backups")


@app.post("/api/backup/restore", response_model=MessageResponse)
async def restore_backup(req: RestoreRequest, current_user = Depends(get_current_user)):
    """Restore database from a backup"""
    try:
        backup_path = os.path.join(BACKUP_DIR, req.filename)
        
        # Validate backup file exists
        if not os.path.exists(backup_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup file not found")
        
        # Validate filename to prevent path traversal
        if ".." in req.filename or "/" in req.filename or "\\" in req.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")
        
        # Create a backup of current database before restoring
        current_backup = f"pre_restore_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(DB_PATH, os.path.join(BACKUP_DIR, current_backup))
        
        # Restore the backup
        shutil.copy2(backup_path, DB_PATH)
        
        logger.info(f"Database restored by user {current_user['email']} from backup: {req.filename}")
        
        return {"message": "Database restored successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Restore failed")


@app.get("/api/backup/download/{filename}")
async def download_backup(filename: str, current_user = Depends(get_current_user)):
    """Download a backup file"""
    try:
        # Validate filename to prevent path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")
        
        backup_path = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(backup_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup file not found")
        
        logger.info(f"Backup downloaded by user {current_user['email']}: {filename}")
        
        return FileResponse(
            path=backup_path,
            filename=filename,
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Download failed")


@app.delete("/api/backup/delete/{filename}", response_model=MessageResponse)
async def delete_backup(filename: str, current_user = Depends(get_current_user)):
    """Delete a backup file"""
    try:
        # Validate filename to prevent path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")
        
        backup_path = os.path.join(BACKUP_DIR, filename)
        
        if not os.path.exists(backup_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup file not found")
        
        os.remove(backup_path)
        
        logger.info(f"Backup deleted by user {current_user['email']}: {filename}")
        
        return {"message": "Backup deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Delete failed")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception(f"Unhandled exception: {exc}")
    return {"error": "Internal server error"}, 500


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)