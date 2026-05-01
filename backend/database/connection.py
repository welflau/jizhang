import aiosqlite
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "bills.db")


async def get_db():
    """
    Dependency to get database connection.
    
    Yields:
        aiosqlite.Connection: Database connection with row factory set.
    """
    async with aiosqlite.connect(DB_PATH, timeout=5.0) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def init_database():
    """
    Initialize database schema and indexes.
    
    Creates tables if they don't exist and applies necessary indexes.
    """
    async with aiosqlite.connect(DB_PATH, timeout=5.0) as db:
        # Create bills table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_type TEXT NOT NULL CHECK(bill_type IN ('income', 'expense')),
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        
        # Apply indexes from migration file
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_bills_date ON bills(date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_bills_category ON bills(category)",
            "CREATE INDEX IF NOT EXISTS idx_bills_type ON bills(bill_type)",
            "CREATE INDEX IF NOT EXISTS idx_bills_amount ON bills(amount)",
            "CREATE INDEX IF NOT EXISTS idx_bills_type_date ON bills(bill_type, date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_bills_category_date ON bills(category, date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_bills_created_at ON bills(created_at DESC)"
        ]
        
        for index_sql in indexes:
            await db.execute(index_sql)
        
        await db.commit()
        logger.info("Database initialized with schema and indexes")
