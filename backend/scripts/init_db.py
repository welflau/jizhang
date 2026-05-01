import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models.base import Base
from app.core.database import engine


async def init_db():
    """Initialize database by creating all tables"""
    print("Starting database initialization...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            print("Dropping existing tables...")
            await conn.run_sync(Base.metadata.drop_all)
            
            print("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
        
        print("✓ Database tables created successfully!")
        
        # Verify connection
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            await result.fetchone()
            print("✓ Database connection verified!")
        
        return True
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False
    finally:
        await engine.dispose()


async def check_db_connection():
    """Check if database connection is working"""
    print("Checking database connection...")
    
    try:
        async with engine.connect() as conn:
            result = await conn.execute("SELECT version()")
            version = await result.fetchone()
            print(f"✓ Connected to PostgreSQL: {version[0]}")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    finally:
        await engine.dispose()


async def main():
    """Main function to run database initialization"""
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    
    # Check connection first
    connection_ok = await check_db_connection()
    if not connection_ok:
        print("\nPlease check your database configuration:")
        print(f"  - DATABASE_URL: {settings.DATABASE_URL}")
        print(f"  - Host: {settings.POSTGRES_HOST}")
        print(f"  - Port: {settings.POSTGRES_PORT}")
        print(f"  - Database: {settings.POSTGRES_DB}")
        print(f"  - User: {settings.POSTGRES_USER}")
        sys.exit(1)
    
    print()
    
    # Initialize database
    init_ok = await init_db()
    if not init_ok:
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Database initialization completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())