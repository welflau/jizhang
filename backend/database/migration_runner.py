"""Database migration runner with version tracking.

Manages schema migrations using a simple version-based system.
Migrations are SQL files named with timestamp prefix: YYYYMMDD_HHMMSS_description.sql
"""

import os
import re
import aiosqlite
from pathlib import Path
from typing import List, Tuple
import logging


logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


async def ensure_migrations_table(conn: aiosqlite.Connection) -> None:
    """Create schema_migrations table if not exists.
    
    Args:
        conn: Active database connection
    """
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            filename TEXT NOT NULL
        )
    """)
    await conn.commit()


async def get_applied_migrations(conn: aiosqlite.Connection) -> set:
    """Get set of already applied migration versions.
    
    Args:
        conn: Active database connection
        
    Returns:
        set: Set of version strings (e.g., {'20240101_000001', ...})
    """
    cursor = await conn.execute("SELECT version FROM schema_migrations ORDER BY version")
    rows = await cursor.fetchall()
    return {row[0] for row in rows}


def get_pending_migrations(applied: set) -> List[Tuple[str, Path]]:
    """Find migration files that haven't been applied yet.
    
    Args:
        applied: Set of applied migration versions
        
    Returns:
        List of (version, filepath) tuples sorted by version
    """
    if not MIGRATIONS_DIR.exists():
        logger.warning(f"Migrations directory not found: {MIGRATIONS_DIR}")
        return []
    
    pending = []
    pattern = re.compile(r"^(\d{8}_\d{6})_.*\.sql$")
    
    for filepath in sorted(MIGRATIONS_DIR.glob("*.sql")):
        match = pattern.match(filepath.name)
        if match:
            version = match.group(1)
            if version not in applied:
                pending.append((version, filepath))
        else:
            logger.warning(f"Invalid migration filename format: {filepath.name}")
    
    return sorted(pending, key=lambda x: x[0])


async def apply_migration(conn: aiosqlite.Connection, version: str, filepath: Path) -> None:
    """Execute a single migration file.
    
    Args:
        conn: Active database connection
        version: Migration version string
        filepath: Path to SQL migration file
        
    Raises:
        Exception: If migration execution fails
    """
    logger.info(f"Applying migration {version}: {filepath.name}")
    
    try:
        sql_content = filepath.read_text(encoding="utf-8")
        
        # Split by semicolon and execute each statement
        # Filter out comments and empty statements
        statements = [
            stmt.strip() 
            for stmt in sql_content.split(";")
            if stmt.strip() and not stmt.strip().startswith("--")
        ]
        
        for statement in statements:
            if statement:
                await conn.execute(statement)
        
        # Record migration as applied
        await conn.execute(
            "INSERT INTO schema_migrations (version, filename) VALUES (?, ?)",
            (version, filepath.name)
        )
        await conn.commit()
        
        logger.info(f"✓ Migration {version} applied successfully")
        
    except Exception as e:
        await conn.rollback()
        logger.exception(f"✗ Migration {version} failed: {e}")
        raise


async def run_migrations(db_path: str) -> None:
    """Run all pending database migrations.
    
    Args:
        db_path: Path to SQLite database file
        
    Raises:
        Exception: If any migration fails
    """
    # Ensure database directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(db_path) as conn:
        # Enable foreign keys and set busy timeout
        await conn.execute("PRAGMA foreign_keys = ON")
        await conn.execute("PRAGMA busy_timeout = 5000")
        
        await ensure_migrations_table(conn)
        applied = await get_applied_migrations(conn)
        pending = get_pending_migrations(applied)
        
        if not pending:
            logger.info("No pending migrations")
            return
        
        logger.info(f"Found {len(pending)} pending migration(s)")
        
        for version, filepath in pending:
            await apply_migration(conn, version, filepath)
        
        logger.info(f"All migrations completed. Current version: {pending[-1][0]}")


async def get_current_version(conn: aiosqlite.Connection) -> str:
    """Get the latest applied migration version.
    
    Args:
        conn: Active database connection
        
    Returns:
        str: Latest version string or 'none' if no migrations applied
    """
    cursor = await conn.execute(
        "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1"
    )
    row = await cursor.fetchone()
    return row[0] if row else "none"
