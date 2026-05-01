"""Database initialization and connection management."""
import sqlite3
import logging

logger = logging.getLogger(__name__)
DB_PATH = 'visitor_data.db'


def get_db_connection():
    """Get SQLite database connection.
    
    Returns:
        sqlite3.Connection: Database connection with row factory
    """
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database schema."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                ip TEXT NOT NULL,
                user_agent TEXT,
                path TEXT,
                method TEXT
            )
        """)
        
        # Create index on timestamp for faster sorting
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_visits_timestamp
            ON visits(timestamp)
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.exception(f"Database initialization failed: {e}")
        raise
