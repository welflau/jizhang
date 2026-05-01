"""Database initialization and connection management."""
import os
import aiosqlite
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "app.db")


async def get_db_connection() -> aiosqlite.Connection:
    """Get database connection with optimized settings.
    
    Returns:
        aiosqlite.Connection: Configured database connection
    """
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON")
    await db.execute("PRAGMA busy_timeout = 5000")
    return db


async def init_db():
    """Initialize database and run migrations."""
    from .migration_runner import run_migrations
    
    # Ensure database directory exists
    db_dir = Path(DB_PATH).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Run migrations
    await run_migrations(DB_PATH)
