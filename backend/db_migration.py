#!/usr/bin/env python3
"""
Database Migration Runner

Executes SQL migration files in order to set up or update the database schema.
Migrations are stored in backend/migrations/ directory and executed sequentially.
"""

import aiosqlite
import asyncio
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "backend/app.db")
MIGRATIONS_DIR = Path("backend/migrations")


async def create_migrations_table(db: aiosqlite.Connection):
    """
    Create migrations tracking table if it doesn't exist.
    
    Args:
        db: Database connection
    """
    await db.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration_file TEXT NOT NULL UNIQUE,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    await db.commit()
    logger.info("Migrations tracking table ready")


async def get_applied_migrations(db: aiosqlite.Connection) -> set:
    """
    Get list of already applied migrations.
    
    Args:
        db: Database connection
        
    Returns:
        Set of migration filenames that have been applied
    """
    cursor = await db.execute("SELECT migration_file FROM schema_migrations")
    rows = await cursor.fetchall()
    return {row[0] for row in rows}


async def apply_migration(db: aiosqlite.Connection, migration_file: Path):
    """
    Apply a single migration file.
    
    Args:
        db: Database connection
        migration_file: Path to migration SQL file
    """
    logger.info(f"Applying migration: {migration_file.name}")
    
    # Read migration SQL
    sql_content = migration_file.read_text(encoding='utf-8')
    
    # Execute migration (split by semicolon for multiple statements)
    try:
        await db.executescript(sql_content)
        
        # Record migration as applied
        await db.execute(
            "INSERT INTO schema_migrations (migration_file) VALUES (?)",
            (migration_file.name,)
        )
        await db.commit()
        logger.info(f"✓ Migration {migration_file.name} applied successfully")
    except Exception as e:
        await db.rollback()
        logger.error(f"✗ Failed to apply migration {migration_file.name}: {e}")
        raise


async def run_migrations():
    """
    Run all pending migrations in order.
    """
    # Ensure migrations directory exists
    if not MIGRATIONS_DIR.exists():
        logger.warning(f"Migrations directory {MIGRATIONS_DIR} does not exist")
        return
    
    # Get all migration files sorted by name (assumes naming like 001_xxx.sql, 002_xxx.sql)
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    
    if not migration_files:
        logger.info("No migration files found")
        return
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Enable foreign keys
        await db.execute("PRAGMA foreign_keys = ON")
        
        # Create migrations tracking table
        await create_migrations_table(db)
        
        # Get already applied migrations
        applied = await get_applied_migrations(db)
        
        # Apply pending migrations
        pending_count = 0
        for migration_file in migration_files:
            if migration_file.name not in applied:
                await apply_migration(db, migration_file)
                pending_count += 1
            else:
                logger.info(f"⊙ Migration {migration_file.name} already applied, skipping")
        
        if pending_count == 0:
            logger.info("All migrations are up to date")
        else:
            logger.info(f"Applied {pending_count} new migration(s)")


async def rollback_last_migration():
    """
    Rollback the last applied migration (for development use).
    Note: This is a simple implementation and doesn't execute DOWN migrations.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT migration_file FROM schema_migrations ORDER BY applied_at DESC LIMIT 1"
        )
        row = await cursor.fetchone()
        
        if not row:
            logger.info("No migrations to rollback")
            return
        
        migration_file = row[0]
        logger.warning(f"Rolling back migration: {migration_file}")
        logger.warning("Note: This only removes the tracking record, not the schema changes")
        
        await db.execute(
            "DELETE FROM schema_migrations WHERE migration_file = ?",
            (migration_file,)
        )
        await db.commit()
        logger.info(f"✓ Migration {migration_file} rollback recorded")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(rollback_last_migration())
    else:
        asyncio.run(run_migrations())
