"""
Database initialization module.
Configures database connection pool, session management, and base models.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from typing import AsyncGenerator
import logging

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create declarative base for models
Base = declarative_base()

# Database engine configuration
engine_kwargs = {
    "echo": settings.DATABASE_ECHO,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
}

# Create async engine for PostgreSQL
if settings.DATABASE_URL.startswith("postgresql"):
    # Convert to async URL if needed
    async_database_url = settings.DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    
    # Configure connection pool
    if settings.ENVIRONMENT == "production":
        engine_kwargs.update({
            "poolclass": QueuePool,
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_timeout": 30,
        })
    else:
        engine_kwargs.update({
            "poolclass": QueuePool,
            "pool_size": 5,
            "max_overflow": 10,
        })
    
    async_engine = create_async_engine(async_database_url, **engine_kwargs)
    
elif settings.DATABASE_URL.startswith("sqlite"):
    # SQLite async configuration
    async_database_url = settings.DATABASE_URL.replace(
        "sqlite://", "sqlite+aiosqlite://"
    )
    engine_kwargs.update({
        "poolclass": NullPool,
        "connect_args": {"check_same_thread": False},
    })
    async_engine = create_async_engine(async_database_url, **engine_kwargs)
    
else:
    raise ValueError(f"Unsupported database URL: {settings.DATABASE_URL}")

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Synchronous engine for migrations and initial setup
sync_database_url = settings.DATABASE_URL
if settings.DATABASE_URL.startswith("postgresql+asyncpg"):
    sync_database_url = settings.DATABASE_URL.replace(
        "postgresql+asyncpg://", "postgresql://"
    )
elif settings.DATABASE_URL.startswith("sqlite+aiosqlite"):
    sync_database_url = settings.DATABASE_URL.replace(
        "sqlite+aiosqlite://", "sqlite://"
    )

sync_engine = create_engine(
    sync_database_url,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.
    Used for FastAPI dependency injection.
    
    Usage:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in models that inherit from Base.
    
    Note: For production, use Alembic migrations instead.
    """
    try:
        async with async_engine.begin() as conn:
            # Import all models here to ensure they are registered with Base
            from app.models import user, agent, task, workflow  # noqa: F401
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


async def close_db() -> None:
    """
    Close database connections.
    Should be called on application shutdown.
    """
    try:
        await async_engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
        raise


def init_db_sync() -> None:
    """
    Synchronous database initialization.
    Used for initial setup and migrations.
    """
    try:
        # Import all models
        from app.models import user, agent, task, workflow  # noqa: F401
        
        # Create all tables
        Base.metadata.create_all(bind=sync_engine)
        logger.info("Database tables created successfully (sync)")
    except Exception as e:
        logger.error(f"Error initializing database (sync): {e}")
        raise


async def check_db_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def get_sync_db():
    """
    Get synchronous database session.
    Used for background tasks and migrations.
    
    Yields:
        Session: Synchronous database session
    """
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Sync database session error: {e}")
        raise
    finally:
        db.close()


# Export commonly used objects
__all__ = [
    "Base",
    "async_engine",
    "sync_engine",
    "AsyncSessionLocal",
    "SyncSessionLocal",
    "get_db",
    "get_sync_db",
    "init_db",
    "init_db_sync",
    "close_db",
    "check_db_connection",
]