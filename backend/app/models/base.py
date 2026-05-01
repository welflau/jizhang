from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings


# 定义命名约定，用于自动生成约束名称
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)


# 创建 Base 模型类
class Base(DeclarativeBase):
    """
    Base class for all database models
    """
    metadata = metadata
    
    # 通用字段
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    def dict(self):
        """
        Convert model instance to dictionary
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


# 创建异步数据库引擎
def get_async_engine():
    """
    Create async database engine with connection pool
    """
    # 根据数据库类型选择不同的驱动
    if settings.DATABASE_URL.startswith("sqlite"):
        # SQLite 使用 aiosqlite
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            poolclass=NullPool,  # SQLite 不需要连接池
            connect_args={"check_same_thread": False}
        )
    else:
        # PostgreSQL 使用 asyncpg
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            poolclass=QueuePool,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,  # 连接前检查连接是否有效
            pool_recycle=3600,  # 1小时后回收连接
        )
    return engine


# 创建同步数据库引擎（用于迁移等操作）
def get_sync_engine():
    """
    Create sync database engine for migrations
    """
    sync_url = settings.DATABASE_URL.replace("+aiosqlite", "").replace("+asyncpg", "+psycopg2")
    
    if sync_url.startswith("sqlite"):
        engine = create_engine(
            sync_url,
            echo=settings.DATABASE_ECHO,
            connect_args={"check_same_thread": False}
        )
    else:
        engine = create_engine(
            sync_url,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
    return engine


# 创建异步引擎实例
async_engine = get_async_engine()

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# 数据库会话依赖注入
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session
    Usage in FastAPI:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
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


# 数据库初始化函数
async def init_db() -> None:
    """
    Initialize database - create all tables
    """
    async with async_engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")


# 数据库删除函数（谨慎使用）
async def drop_db() -> None:
    """
    Drop all database tables (use with caution!)
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("⚠️  All database tables dropped")


# 检查数据库连接
async def check_db_connection() -> bool:
    """
    Check if database connection is working
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


# 关闭数据库连接
async def close_db_connection() -> None:
    """
    Close database connection pool
    """
    await async_engine.dispose()
    print("✅ Database connection pool closed")


# 同步版本的初始化函数（用于脚本）
def init_db_sync() -> None:
    """
    Synchronous version of init_db for scripts
    """
    sync_engine = get_sync_engine()
    Base.metadata.create_all(bind=sync_engine)
    print("✅ Database tables created successfully (sync)")
    sync_engine.dispose()


def drop_db_sync() -> None:
    """
    Synchronous version of drop_db for scripts
    """
    sync_engine = get_sync_engine()
    Base.metadata.drop_all(bind=sync_engine)
    print("⚠️  All database tables dropped (sync)")
    sync_engine.dispose()