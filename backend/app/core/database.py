from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    poolclass=AsyncAdaptedQueuePool if settings.DATABASE_POOL_SIZE > 0 else NullPool,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.
    
    Usage in FastAPI endpoints:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
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
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    This function should be called on application startup.
    For production, use Alembic migrations instead.
    """
    try:
        async with engine.begin() as conn:
            # Import all models here to ensure they are registered with Base
            from app.models import user, task, project  # noqa: F401
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


async def close_db() -> None:
    """
    Close database connection pool.
    
    This function should be called on application shutdown.
    """
    try:
        await engine.dispose()
        logger.info("Database connection pool closed")
    except Exception as e:
        logger.error(f"Error closing database connection pool: {str(e)}")
        raise


async def check_db_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False


async def drop_all_tables() -> None:
    """
    Drop all tables from database.
    
    WARNING: This will delete all data! Use only in development/testing.
    """
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("Cannot drop tables in production environment")
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Error dropping database tables: {str(e)}")
        raise


async def reset_db() -> None:
    """
    Reset database by dropping and recreating all tables.
    
    WARNING: This will delete all data! Use only in development/testing.
    """
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("Cannot reset database in production environment")
    
    await drop_all_tables()
    await init_db()
    logger.warning("Database reset completed")


# Database session context manager for manual usage
class DatabaseSession:
    """
    Context manager for database sessions outside of FastAPI dependency injection.
    
    Usage:
        async with DatabaseSession() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
    """
    
    def __init__(self):
        self.session: AsyncSession | None = None
    
    async def __aenter__(self) -> AsyncSession:
        self.session = AsyncSessionLocal()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()


# Export commonly used items
__all__ = [
    "Base",
    "engine",
    "AsyncSessionLocal",
    "get_db",
    "init_db",
    "close_db",
    "check_db_connection",
    "drop_all_tables",
    "reset_db",
    "DatabaseSession",
]