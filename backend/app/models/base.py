from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    poolclass=AsyncAdaptedQueuePool if settings.DATABASE_POOL_SIZE > 0 else NullPool,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# 声明式基类
class Base(DeclarativeBase):
    """
    所有数据库模型的基类
    """
    pass


# 数据库会话依赖注入
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数
    用于 FastAPI 路由中的依赖注入
    
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


# 数据库初始化函数
async def init_db() -> None:
    """
    初始化数据库，创建所有表
    """
    try:
        async with engine.begin() as conn:
            # 导入所有模型以确保它们被注册
            from app.models import user, task, agent  # noqa: F401
            
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


# 数据库连接测试
async def check_db_connection() -> bool:
    """
    检查数据库连接是否正常
    
    Returns:
        bool: 连接成功返回 True，否则返回 False
    """
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


# 关闭数据库连接
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


# 数据库会话上下文管理器
class DatabaseSession:
    """
    数据库会话上下文管理器
    用于在非 FastAPI 路由中使用数据库会话
    
    使用示例:
        async with DatabaseSession() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
    """
    
    def __init__(self):
        self.session: AsyncSession = None
    
    async def __aenter__(self) -> AsyncSession:
        self.session = AsyncSessionLocal()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()


# 数据库迁移辅助函数
async def drop_all_tables() -> None:
    """
    删除所有表（谨慎使用，仅用于开发环境）
    """
    if settings.ENVIRONMENT != "development":
        raise RuntimeError("drop_all_tables can only be used in development environment")
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Error dropping database tables: {str(e)}")
        raise


async def reset_database() -> None:
    """
    重置数据库（删除所有表后重新创建，仅用于开发环境）
    """
    if settings.ENVIRONMENT != "development":
        raise RuntimeError("reset_database can only be used in development environment")
    
    await drop_all_tables()
    await init_db()
    logger.info("Database reset completed")