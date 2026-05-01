from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool
from typing import AsyncGenerator, Generator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# 同步数据库引擎（用于迁移和初始化）
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DB_ECHO,
)

# 同步会话工厂
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    class_=Session,
)

# 异步数据库引擎
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DB_ECHO,
    future=True,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# 同步数据库会话依赖注入
def get_db() -> Generator[Session, None, None]:
    """
    同步数据库会话依赖
    用于 FastAPI 路由中的依赖注入
    """
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()


# 异步数据库会话依赖注入
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    异步数据库会话依赖
    用于 FastAPI 异步路由中的依赖注入
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Async database session error: {str(e)}")
            raise
        finally:
            await session.close()


# 测试数据库连接
def test_db_connection() -> bool:
    """
    测试同步数据库连接是否正常
    """
    try:
        with sync_engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✓ Sync database connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ Sync database connection failed: {str(e)}")
        return False


async def test_async_db_connection() -> bool:
    """
    测试异步数据库连接是否正常
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("✓ Async database connection successful")
        return True
    except Exception as e:
        logger.error(f"✗ Async database connection failed: {str(e)}")
        return False


# 关闭数据库连接
async def close_db_connections():
    """
    关闭所有数据库连接
    用于应用关闭时清理资源
    """
    try:
        await async_engine.dispose()
        sync_engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")


# 获取数据库会话上下文管理器（用于非依赖注入场景）
class DatabaseSession:
    """
    数据库会话上下文管理器
    用于在非 FastAPI 路由中使用数据库会话
    """
    
    def __init__(self, async_mode: bool = False):
        self.async_mode = async_mode
        self.session = None
    
    def __enter__(self) -> Session:
        if self.async_mode:
            raise RuntimeError("Use async context manager for async sessions")
        self.session = SyncSessionLocal()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
    
    async def __aenter__(self) -> AsyncSession:
        if not self.async_mode:
            raise RuntimeError("Use sync context manager for sync sessions")
        self.session = AsyncSessionLocal()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()


# 数据库健康检查
async def check_db_health() -> dict:
    """
    检查数据库健康状态
    返回连接池状态和连接测试结果
    """
    health_status = {
        "database": "unknown",
        "sync_connection": False,
        "async_connection": False,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
    }
    
    try:
        # 测试同步连接
        health_status["sync_connection"] = test_db_connection()
        
        # 测试异步连接
        health_status["async_connection"] = await test_async_db_connection()
        
        # 判断整体状态
        if health_status["sync_connection"] and health_status["async_connection"]:
            health_status["database"] = "healthy"
        else:
            health_status["database"] = "unhealthy"
            
    except Exception as e:
        health_status["database"] = "error"
        health_status["error"] = str(e)
        logger.error(f"Database health check failed: {str(e)}")
    
    return health_status


# 初始化数据库连接（应用启动时调用）
async def init_db():
    """
    初始化数据库连接
    在应用启动时调用，测试连接并记录日志
    """
    logger.info("Initializing database connections...")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"Pool size: {settings.DB_POOL_SIZE}")
    logger.info(f"Max overflow: {settings.DB_MAX_OVERFLOW}")
    
    # 测试连接
    sync_ok = test_db_connection()
    async_ok = await test_async_db_connection()
    
    if sync_ok and async_ok:
        logger.info("✓ Database initialization successful")
    else:
        logger.warning("⚠ Database initialization completed with warnings")