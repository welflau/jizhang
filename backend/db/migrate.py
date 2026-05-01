#!/usr/bin/env python3
"""
Database migration runner for SQLite.

Usage:
    python migrate.py          # Run all pending migrations
    python migrate.py --reset  # Drop all tables and re-run migrations
"""

import asyncio
import os
import sys
from pathlib import Path
import aiosqlite
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DB_PATH = os.getenv("DB_PATH", "backend/data/app.db")
MIGRATIONS_DIR = Path("backend/migrations")


async def get_applied_migrations(db: aiosqlite.Connection) -> set:
    """
    Get list of already applied migration versions.
    
    Args:
        db: Database connection
        
    Returns:
        Set of applied migration versions
    """
    try:
        cursor = await db.execute("SELECT version FROM schema_migrations ORDER BY version")
        rows = await cursor.fetchall()
        return {row[0] for row in rows}
    except aiosqlite.OperationalError:
        # Table doesn't exist yet
        return set()


async def get_migration_files() -> list:
    """
    Get sorted list of migration files from migrations directory.
    
    Returns:
        List of tuples (version, file_path)
    """
    if not MIGRATIONS_DIR.exists():
        logger.warning(f"Migrations directory not found: {MIGRATIONS_DIR}")
        return []
    
    migrations = []
    for file_path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        # Extract version from filename (e.g., "001_init_schema.sql" -> "001")
        version = file_path.stem.split('_')[0]
        migrations.append((version, file_path))
    
    return sorted(migrations, key=lambda x: x[0])


async def run_migration(db: aiosqlite.Connection, version: str, file_path: Path) -> bool:
    """
    Execute a single migration file.
    
    Args:
        db: Database connection
        version: Migration version
        file_path: Path to migration SQL file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Running migration {version}: {file_path.name}")
        
        # Read migration file
        sql_content = file_path.read_text(encoding='utf-8')
        
        # Execute migration (split by semicolon to handle multiple statements)
        await db.executescript(sql_content)
        await db.commit()
        
        logger.info(f"✓ Migration {version} applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Migration {version} failed: {e}")
        await db.rollback()
        return False


async def reset_database(db: aiosqlite.Connection):
    """
    Drop all tables and reset database to clean state.
    
    Args:
        db: Database connection
    """
    logger.warning("Resetting database - dropping all tables...")
    
    # Get all table names
    cursor = await db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    tables = await cursor.fetchall()
    
    # Drop all tables
    for (table_name,) in tables:
        await db.execute(f"DROP TABLE IF EXISTS {table_name}")
        logger.info(f"Dropped table: {table_name}")
    
    await db.commit()
    logger.info("Database reset complete")


async def run_migrations(reset: bool = False):
    """
    Run all pending database migrations.
    
    Args:
        reset: If True, drop all tables before running migrations
    """
    # Ensure data directory exists
    db_dir = Path(DB_PATH).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Enable foreign keys
        await db.execute("PRAGMA foreign_keys = ON")
        
        # Reset database if requested
        if reset:
            await reset_database(db)
        
        # Get applied migrations
        applied = await get_applied_migrations(db)
        logger.info(f"Applied migrations: {sorted(applied) if applied else 'none'}")
        
        # Get all migration files
        migrations = await get_migration_files()
        if not migrations:
            logger.warning("No migration files found")
            return
        
        logger.info(f"Found {len(migrations)} migration file(s)")
        
        # Run pending migrations
        pending_count = 0
        for version, file_path in migrations:
            if version not in applied:
                success = await run_migration(db, version, file_path)
                if not success:
                    logger.error("Migration failed - stopping")
                    sys.exit(1)
                pending_count += 1
        
        if pending_count == 0:
            logger.info("No pending migrations - database is up to date")
        else:
            logger.info(f"Successfully applied {pending_count} migration(s)")


if __name__ == "__main__":
    # Parse command line arguments
    reset_flag = "--reset" in sys.argv
    
    # Run migrations
    asyncio.run(run_migrations(reset=reset_flag))
