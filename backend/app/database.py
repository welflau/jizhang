import os
import aiosqlite
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "./data/app.db")

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

async def init_db():
    """Initialize database schema"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                ip TEXT NOT NULL,
                user_agent TEXT,
                path TEXT
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON access_logs(timestamp)
        """)
        await db.commit()
        logger.info(f"Database initialized at {DB_PATH}")

@asynccontextmanager
async def get_db():
    """Async context manager for database connection"""
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    try:
        yield conn
    finally:
        await conn.close()
