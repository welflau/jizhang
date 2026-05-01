import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.models.base import Base

logger = logging.getLogger(__name__)


# 同步引擎（用于初始化和迁移）
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DB_ECHO,
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


# 异步引擎（用于应用运行时）
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    echo=settings.DB_ECHO,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def init_db() -> None:
    """
    初始化数据库
    创建所有表（如果不存在）
    """
    try:
        logger.info("开始初始化数据库...")
        logger.info(f"数据库连接: {settings.SYNC_DATABASE_URL.split('@')[-1]}")
        
        # 测试数据库连接
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("数据库连接测试成功")
        
        # 创建所有表
        Base.metadata.create_all(bind=sync_engine)
        logger.info("数据库表创建成功")
        
        # 打印所有创建的表
        tables = Base.metadata.tables.keys()
        if tables:
            logger.info(f"已创建的表: {', '.join(tables)}")
        else:
            logger.warning("没有检测到任何模型表")
            
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise


def drop_db() -> None:
    """
    删除所有数据库表
    警告：此操作会删除所有数据！
    """
    try:
        logger.warning("开始删除所有数据库表...")
        Base.metadata.drop_all(bind=sync_engine)
        logger.info("数据库表删除成功")
    except Exception as e:
        logger.error(f"数据库表删除失败: {str(e)}")
        raise


def reset_db() -> None:
    """
    重置数据库
    删除所有表并重新创建
    警告：此操作会删除所有数据！
    """
    try:
        logger.warning("开始重置数据库...")
        drop_db()
        init_db()
        logger.info("数据库重置成功")
    except Exception as e:
        logger.error(f"数据库重置失败: {str(e)}")
        raise


async def check_db_connection() -> bool:
    """
    检查异步数据库连接是否正常
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("异步数据库连接检查成功")
        return True
    except Exception as e:
        logger.error(f"异步数据库连接检查失败: {str(e)}")
        return False


def get_sync_db():
    """
    同步数据库会话依赖注入
    用于同步操作（如脚本、初始化等）
    """
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """
    异步数据库会话依赖注入
    用于 FastAPI 路由处理
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def close_db_connections():
    """
    关闭所有数据库连接
    用于应用关闭时清理资源
    """
    try:
        await async_engine.dispose()
        sync_engine.dispose()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {str(e)}")


if __name__ == "__main__":
    """
    直接运行此脚本可以初始化数据库
    """
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            init_db()
            print("✓ 数据库初始化完成")
        elif command == "drop":
            confirm = input("确认要删除所有表吗？(yes/no): ")
            if confirm.lower() == "yes":
                drop_db()
                print("✓ 数据库表已删除")
            else:
                print("操作已取消")
        elif command == "reset":
            confirm = input("确认要重置数据库吗？这将删除所有数据！(yes/no): ")
            if confirm.lower() == "yes":
                reset_db()
                print("✓ 数据库已重置")
            else:
                print("操作已取消")
        else:
            print(f"未知命令: {command}")
            print("可用命令: init, drop, reset")
    else:
        init_db()
        print("✓ 数据库初始化完成")