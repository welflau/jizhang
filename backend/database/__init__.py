from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库配置
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/finance_tracker"
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖注入函数
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库，创建所有表
    """
    from backend.database.models import Category
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    删除所有表（仅用于开发环境）
    """
    Base.metadata.drop_all(bind=engine)