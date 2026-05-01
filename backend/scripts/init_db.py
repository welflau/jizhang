#!/usr/bin/env python3
"""Database initialization script.

This script creates all database tables defined in models.
Run this script manually to initialize or reset the database:

    python scripts/init_db.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db, close_db, engine
from app.models.base import Base
from app.core.config import get_settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main initialization function."""
    settings = get_settings()
    
    logger.info("=" * 60)
    logger.info("Database Initialization Script")
    logger.info("=" * 60)
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"Tables to create: {list(Base.metadata.tables.keys())}")
    logger.info("=" * 60)
    
    try:
        # Initialize database and create all tables
        await init_db()
        
        # Verify tables were created
        async with engine.begin() as conn:
            def get_table_names(connection):
                from sqlalchemy import inspect
                inspector = inspect(connection)
                return inspector.get_table_names()
            
            tables = await conn.run_sync(get_table_names)
            logger.info(f"Created tables: {tables}")
        
        logger.info("=" * 60)
        logger.info("✓ Database initialization completed successfully")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"✗ Database initialization failed: {e}")
        logger.error("=" * 60)
        raise
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
