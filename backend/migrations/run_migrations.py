"""Database migration runner for SQLite."""
import aiosqlite
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent
DB_PATH = os.getenv("DB_PATH", "app.db")


async def run_migrations():
    """Execute all SQL migration files in order."""
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    
    if not migration_files:
        logger.info("No migration files found")
        return
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Enable foreign key constraints
        await db.execute("PRAGMA foreign_keys = ON")
        
        # Create migrations tracking table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        await db.commit()
        
        # Get already applied migrations
        cursor = await db.execute("SELECT filename FROM schema_migrations")
        applied = {row[0] for row in await cursor.fetchall()}
        
        # Run pending migrations
        for migration_file in migration_files:
            filename = migration_file.name
            
            if filename in applied:
                logger.info(f"Skipping already applied migration: {filename}")
                continue
            
            logger.info(f"Applying migration: {filename}")
            
            try:
                sql_content = migration_file.read_text(encoding="utf-8")
                
                # Execute migration (split by semicolon for multiple statements)
                await db.executescript(sql_content)
                
                # Record migration as applied
                await db.execute(
                    "INSERT INTO schema_migrations (filename) VALUES (?)",
                    (filename,)
                )
                await db.commit()
                
                logger.info(f"Successfully applied migration: {filename}")
                
            except Exception as e:
                logger.error(f"Failed to apply migration {filename}: {e}")
                await db.rollback()
                raise


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_migrations())
