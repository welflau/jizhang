import aiosqlite
import os
from contextlib import asynccontextmanager


DATABASE_PATH = os.getenv("DATABASE_PATH", "app.db")


async def init_db():
    """Initialize database schema."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                phone TEXT UNIQUE,
                hashed_password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                CONSTRAINT email_or_phone CHECK (email IS NOT NULL OR phone IS NOT NULL)
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)
        """)
        await db.commit()


@asynccontextmanager
async def get_db():
    """Database connection dependency.
    
    Yields:
        aiosqlite.Connection with row_factory set to Row
    """
    async with aiosqlite.connect(DATABASE_PATH, timeout=5.0) as db:
        db.row_factory = aiosqlite.Row
        yield db
