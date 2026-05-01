from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy Base 模型类"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    数据库会话依赖注入
    用于 FastAPI 路由中获取数据库会话
    
    使用示例:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
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
    初始化数据库
    创建所有表（仅用于开发环境，生产环境建议使用 Alembic 迁移）
    """
    try:
        async with engine.begin() as conn:
            # 导入所有模型以确保它们被注册
            from app.models import user, project, task, file, chat  # noqa
            
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


async def close_db() -> None:
    """
    关闭数据库连接池
    应用关闭时调用
    """
    try:
        await engine.dispose()
        logger.info("Database connection pool closed")
    except Exception as e:
        logger.error(f"Error closing database connection pool: {str(e)}")
        raise


async def check_db_connection() -> bool:
    """
    检查数据库连接是否正常
    返回 True 表示连接正常，False 表示连接失败
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            logger.info("Database connection check successful")
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False


# 可选：Redis 连接依赖（用于缓存和会话管理）
try:
    from redis.asyncio import Redis
    
    redis_client: Redis | None = None
    
    async def get_redis() -> Redis:
        """
        Redis 连接依赖注入
        """
        global redis_client
        if redis_client is None:
            redis_client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
        return redis_client
    
    async def close_redis() -> None:
        """
        关闭 Redis 连接
        """
        global redis_client
        if redis_client:
            await redis_client.close()
            logger.info("Redis connection closed")
            
except ImportError:
    logger.warning("Redis library not installed, Redis features will be disabled")
    
    async def get_redis():
        raise NotImplementedError("Redis is not configured")
    
    async def close_redis():
        pass
