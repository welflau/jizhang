"""Database connection and initialization."""
import aiosqlite
import os
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "app.db")
BUSY_TIMEOUT = 5000  # 5 seconds


@asynccontextmanager
async def get_db():
    """Async context manager for database connections.
    
    Yields:
        aiosqlite.Connection: Database connection with foreign keys enabled
    """
    conn = await aiosqlite.connect(DB_PATH, timeout=BUSY_TIMEOUT)
    conn.row_factory = aiosqlite.Row  # Enable dict-like row access
    
    try:
        # Enable foreign key constraints
        await conn.execute("PRAGMA foreign_keys = ON")
        # Enable WAL mode for better concurrency
        await conn.execute("PRAGMA journal_mode = WAL")
        yield conn
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        await conn.close()


async def init_db():
    """Initialize database by running migrations."""
    from backend.migrations.run_migrations import run_migrations
    
    logger.info("Initializing database...")
    await run_migrations()
    logger.info("Database initialized successfully")
