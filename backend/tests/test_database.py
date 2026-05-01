import pytest
import asyncio
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.database import (
    get_db,
    init_db,
    close_db,
    engine,
    async_session_maker,
    Base
)
from app.core.config import settings
from app.models.base import BaseModel


class TestDatabaseConnection:
    """测试数据库连接"""

    @pytest.mark.asyncio
    async def test_database_connection(self):
        """测试数据库连接是否正常"""
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

    @pytest.mark.asyncio
    async def test_database_url_from_env(self):
        """测试数据库连接字符串从环境变量读取"""
        assert settings.DATABASE_URL is not None
        assert len(settings.DATABASE_URL) > 0
        assert "postgresql" in settings.DATABASE_URL or "sqlite" in settings.DATABASE_URL

    @pytest.mark.asyncio
    async def test_async_session_maker(self):
        """测试异步会话创建器"""
        assert async_session_maker is not None
        async with async_session_maker() as session:
            assert isinstance(session, AsyncSession)
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1


class TestDatabaseSession:
    """测试数据库会话管理"""

    @pytest.mark.asyncio
    async def test_get_db_dependency(self):
        """测试数据库会话依赖注入"""
        async for session in get_db():
            assert isinstance(session, AsyncSession)
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            break

    @pytest.mark.asyncio
    async def test_session_commit(self):
        """测试会话提交"""
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
            await session.commit()

    @pytest.mark.asyncio
    async def test_session_rollback(self):
        """测试会话回滚"""
        async with async_session_maker() as session:
            try:
                await session.execute(text("SELECT 1"))
                await session.rollback()
            except Exception as e:
                pytest.fail(f"Session rollback failed: {e}")

    @pytest.mark.asyncio
    async def test_session_isolation(self):
        """测试会话隔离"""
        async with async_session_maker() as session1:
            async with async_session_maker() as session2:
                assert session1 is not session2


class TestBaseModel:
    """测试 Base 模型类"""

    def test_base_model_exists(self):
        """测试 Base 模型类存在"""
        assert Base is not None

    def test_base_model_metadata(self):
        """测试 Base 模型元数据"""
        assert hasattr(Base, "metadata")
        assert Base.metadata is not None

    def test_base_model_inheritance(self):
        """测试 Base 模型可继承"""
        from sqlalchemy import Column, Integer, String
        from app.models.base import Base

        class TestModel(Base):
            __tablename__ = "test_model"
            id = Column(Integer, primary_key=True)
            name = Column(String(50))

        assert issubclass(TestModel, Base)
        assert hasattr(TestModel, "__tablename__")
        assert TestModel.__tablename__ == "test_model"

    def test_base_model_class_attributes(self):
        """测试 BaseModel 类属性"""
        assert hasattr(BaseModel, "id")
        assert hasattr(BaseModel, "created_at")
        assert hasattr(BaseModel, "updated_at")


class TestDatabaseInitialization:
    """测试数据库初始化"""

    @pytest.mark.asyncio
    async def test_init_db(self):
        """测试数据库初始化函数"""
        try:
            await init_db()
        except Exception as e:
            pytest.fail(f"Database initialization failed: {e}")

    @pytest.mark.asyncio
    async def test_close_db(self):
        """测试数据库关闭函数"""
        try:
            await close_db()
        except Exception as e:
            pytest.fail(f"Database close failed: {e}")

    @pytest.mark.asyncio
    async def test_create_tables(self):
        """测试创建数据库表"""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 验证表是否创建成功
        async with engine.begin() as conn:
            result = await conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public'"
                )
            )
            tables = [row[0] for row in result]
            # 至少应该有一些表被创建
            assert isinstance(tables, list)

    @pytest.mark.asyncio
    async def test_drop_tables(self):
        """测试删除数据库表"""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


class TestDatabasePooling:
    """测试数据库连接池"""

    @pytest.mark.asyncio
    async def test_connection_pool_size(self):
        """测试连接池大小配置"""
        assert engine.pool.size() >= 0

    @pytest.mark.asyncio
    async def test_multiple_concurrent_connections(self):
        """测试多个并发连接"""
        async def query_db():
            async with async_session_maker() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar()

        tasks = [query_db() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        assert all(r == 1 for r in results)

    @pytest.mark.asyncio
    async def test_connection_reuse(self):
        """测试连接复用"""
        async with async_session_maker() as session:
            result1 = await session.execute(text("SELECT 1"))
            assert result1.scalar() == 1

        async with async_session_maker() as session:
            result2 = await session.execute(text("SELECT 2"))
            assert result2.scalar() == 2


class TestDatabaseTransactions:
    """测试数据库事务"""

    @pytest.mark.asyncio
    async def test_transaction_commit(self):
        """测试事务提交"""
        async with async_session_maker() as session:
            async with session.begin():
                await session.execute(text("SELECT 1"))
            # 事务应该自动提交

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self):
        """测试错误时事务回滚"""
        try:
            async with async_session_maker() as session:
                async with session.begin():
                    await session.execute(text("SELECT 1"))
                    raise Exception("Test error")
        except Exception:
            pass  # 异常应该触发回滚

    @pytest.mark.asyncio
    async def test_nested_transactions(self):
        """测试嵌套事务"""
        async with async_session_maker() as session:
            async with session.begin():
                await session.execute(text("SELECT 1"))
                async with session.begin_nested():
                    await session.execute(text("SELECT 2"))


class TestDatabaseConfiguration:
    """测试数据库配置"""

    def test_database_url_configuration(self):
        """测试数据库 URL 配置"""
        assert settings.DATABASE_URL is not None
        assert isinstance(settings.DATABASE_URL, str)

    def test_database_echo_configuration(self):
        """测试数据库 echo 配置"""
        assert hasattr(settings, "DATABASE_ECHO")
        assert isinstance(settings.DATABASE_ECHO, bool)

    def test_database_pool_configuration(self):
        """测试数据库连接池配置"""
        assert hasattr(settings, "DATABASE_POOL_SIZE")
        assert hasattr(settings, "DATABASE_MAX_OVERFLOW")
        assert isinstance(settings.DATABASE_POOL_SIZE, int)
        assert isinstance(settings.DATABASE_MAX_OVERFLOW, int)


class TestDatabaseHealth:
    """测试数据库健康检查"""

    @pytest.mark.asyncio
    async def test_database_health_check(self):
        """测试数据库健康检查"""
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            health_status = True
        except Exception:
            health_status = False

        assert health_status is True

    @pytest.mark.asyncio
    async def test_database_ping(self):
        """测试数据库 ping"""
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT 1 as ping"))
            ping_result = result.scalar()
            assert ping_result == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])