#!/usr/bin/env python3
"""Database migration runner for SQLite.

Executes SQL migration files in order and tracks applied migrations.
"""

import asyncio
import aiosqlite
import os
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "app.db")
MIGRATIONS_DIR = Path(__file__).parent


async def init_migrations_table(db: aiosqlite.Connection):
    """Create migrations tracking table if not exists.
    
    Args:
        db: Database connection
    """
    await db.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    await db.commit()
    logger.info("Migrations tracking table initialized")


async def get_applied_migrations(db: aiosqlite.Connection) -> set:
    """Get list of already applied migration filenames.
    
    Args:
        db: Database connection
        
    Returns:
        Set of applied migration filenames
    """
    cursor = await db.execute("SELECT filename FROM schema_migrations")
    rows = await cursor.fetchall()
    return {row[0] for row in rows}


async def apply_migration(db: aiosqlite.Connection, filepath: Path):
    """Apply a single migration file.
    
    Args:
        db: Database connection
        filepath: Path to migration SQL file
        
    Raises:
        Exception: If migration fails
    """
    filename = filepath.name
    logger.info(f"Applying migration: {filename}")
    
    try:
        # Read and execute migration SQL
        sql_content = filepath.read_text(encoding='utf-8')
        await db.executescript(sql_content)
        
        # Record migration as applied
        await db.execute(
            "INSERT INTO schema_migrations (filename) VALUES (?)",
            (filename,)
        )
        await db.commit()
        logger.info(f"✓ Migration applied: {filename}")
        
    except Exception as e:
        await db.rollback()
        logger.error(f"✗ Migration failed: {filename} - {e}")
        raise


async def run_migrations():
    """Run all pending migrations in order."""
    logger.info(f"Starting migrations for database: {DB_PATH}")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Enable foreign keys
        await db.execute("PRAGMA foreign_keys = ON")
        
        # Initialize migrations tracking
        await init_migrations_table(db)
        
        # Get applied migrations
        applied = await get_applied_migrations(db)
        logger.info(f"Already applied: {len(applied)} migrations")
        
        # Find all migration files
        migration_files = sorted(
            [f for f in MIGRATIONS_DIR.glob("*.sql") if f.is_file()]
        )
        
        if not migration_files:
            logger.warning("No migration files found")
            return
        
        # Apply pending migrations
        pending_count = 0
        for filepath in migration_files:
            if filepath.name not in applied:
                await apply_migration(db, filepath)
                pending_count += 1
        
        if pending_count == 0:
            logger.info("No pending migrations")
        else:
            logger.info(f"Applied {pending_count} new migration(s)")


if __name__ == "__main__":
    try:
        asyncio.run(run_migrations())
        logger.info("Migration completed successfully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
