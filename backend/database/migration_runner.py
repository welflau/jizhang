"""Database migration runner with version tracking."""
import aiosqlite
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


async def get_current_version(db: aiosqlite.Connection) -> int:
    """Get current schema version from database.
    
    Args:
        db: Database connection
        
    Returns:
        int: Current schema version (0 if no migrations table exists)
    """
    try:
        cursor = await db.execute(
            "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1"
        )
        row = await cursor.fetchone()
        return row[0] if row else 0
    except aiosqlite.OperationalError:
        # Table doesn't exist yet
        return 0


async def create_migrations_table(db: aiosqlite.Connection):
    """Create schema_migrations tracking table.
    
    Args:
        db: Database connection
    """
    await db.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT
        )
    """)
    await db.commit()


async def get_pending_migrations(current_version: int) -> List[Tuple[int, Path]]:
    """Get list of pending migration files.
    
    Args:
        current_version: Current schema version
        
    Returns:
        List of (version, file_path) tuples sorted by version
    """
    migrations = []
    
    if not MIGRATIONS_DIR.exists():
        logger.warning(f"Migrations directory not found: {MIGRATIONS_DIR}")
        return migrations
    
    for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
        try:
            # Extract version from filename (e.g., "001_create_categories.sql" -> 1)
            version_str = sql_file.stem.split("_")[0]
            version = int(version_str)
            
            if version > current_version:
                migrations.append((version, sql_file))
        except (ValueError, IndexError) as e:
            logger.warning(f"Invalid migration filename {sql_file.name}: {e}")
            continue
    
    return sorted(migrations, key=lambda x: x[0])


async def apply_migration(db: aiosqlite.Connection, version: int, sql_file: Path):
    """Apply a single migration file.
    
    Args:
        db: Database connection
        version: Migration version number
        sql_file: Path to SQL migration file
        
    Raises:
        Exception: If migration fails (will rollback transaction)
    """
    logger.info(f"Applying migration {version}: {sql_file.name}")
    
    # Read SQL file
    sql_content = sql_file.read_text(encoding="utf-8")
    
    # Execute migration in transaction
    try:
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql_content.split(";") if s.strip()]
        
        for statement in statements:
            # Skip comments
            if statement.startswith("--"):
                continue
            await db.execute(statement)
        
        # Record migration
        await db.execute(
            "INSERT INTO schema_migrations (version, description) VALUES (?, ?)",
            (version, sql_file.stem)
        )
        
        await db.commit()
        logger.info(f"Migration {version} applied successfully")
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Migration {version} failed: {e}")
        raise


async def verify_table_structure(db: aiosqlite.Connection, table_name: str):
    """Verify table structure after migration (for debugging).
    
    Args:
        db: Database connection
        table_name: Name of table to verify
    """
    try:
        cursor = await db.execute(f"PRAGMA table_info({table_name})")
        columns = await cursor.fetchall()
        
        logger.info(f"Table '{table_name}' structure:")
        for col in columns:
            logger.info(f"  {col[1]} {col[2]} (nullable={not col[3]}, default={col[4]})")
        
        # Check indexes
        cursor = await db.execute(f"PRAGMA index_list({table_name})")
        indexes = await cursor.fetchall()
        
        logger.info(f"Table '{table_name}' indexes:")
        for idx in indexes:
            logger.info(f"  {idx[1]} (unique={idx[2]})")
            
    except Exception as e:
        logger.warning(f"Could not verify table structure: {e}")


async def run_migrations(db_path: str):
    """Run all pending database migrations.
    
    Args:
        db_path: Path to SQLite database file
        
    Raises:
        Exception: If any migration fails
    """
    async with aiosqlite.connect(db_path) as db:
        # Enable foreign keys
        await db.execute("PRAGMA foreign_keys = ON")
        
        # Create migrations tracking table
        await create_migrations_table(db)
        
        # Get current version
        current_version = await get_current_version(db)
        logger.info(f"Current schema version: {current_version}")
        
        # Get pending migrations
        pending = await get_pending_migrations(current_version)
        
        if not pending:
            logger.info("No pending migrations")
            return
        
        logger.info(f"Found {len(pending)} pending migration(s)")
        
        # Apply each migration
        for version, sql_file in pending:
            await apply_migration(db, version, sql_file)
            
            # Verify structure for categories table
            if "categories" in sql_file.name:
                await verify_table_structure(db, "categories")
        
        logger.info("All migrations completed successfully")
