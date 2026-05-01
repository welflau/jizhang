"""Database initialization and connection management.

Provides async SQLite connection utilities and migration runner integration.
"""

import os
import aiosqlite
from pathlib import Path


DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/app.db")


async def get_db_connection() -> aiosqlite.Connection:
    """Create and return a new database connection.
    
    Returns:
        aiosqlite.Connection: Async SQLite connection with row factory enabled
    """
    db_path = Path(DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = await aiosqlite.connect(str(db_path))
    conn.row_factory = aiosqlite.Row
    # Enable foreign key constraints
    await conn.execute("PRAGMA foreign_keys = ON")
    # Set busy timeout to 5 seconds to prevent "database is locked" errors
    await conn.execute("PRAGMA busy_timeout = 5000")
    return conn


async def init_database():
    """Initialize database and run migrations.
    
    Called during application startup to ensure schema is up-to-date.
    """
    from .migration_runner import run_migrations
    await run_migrations(DATABASE_PATH)
