"""Database connection and session management.

Provides async database engine and session factory for SQLAlchemy ORM.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models import Base

# Database URL from environment variable or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./finance_app.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging during development
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    """Initialize database tables.

    Creates all tables defined in Base metadata if they don't exist.
    Should be called on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency for FastAPI routes to get database session.

    Yields:
        AsyncSession: Database session that auto-closes after request.

    Example:
        @app.get("/users")
        async def list_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
