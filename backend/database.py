backend/database.py

import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Enum, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import enum

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finance_tracker.db")

# 创建数据库引擎
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


# 定义枚举类型
class CategoryType(enum.Enum):
    income = "income"
    expense = "expense"


# 定义 Category 模型
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum(CategoryType), nullable=False)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)

    # 创建复合索引以优化查询性能
    __table_args__ = (
        Index("idx_user_type", "user_id", "type"),
        Index("idx_user_default", "user_id", "is_default"),
    )

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type.value}', user_id={self.user_id})>"


# 数据库依赖项
def get_db():
    """
    获取数据库会话的依赖项函数
    用于 FastAPI 的依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 初始化数据库
def init_db():
    """
    初始化数据库，创建所有表
    """
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


# 数据库迁移脚本
def migrate_database():
    """
    数据库迁移脚本
    用于创建或更新数据库表结构
    """
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if "categories" not in existing_tables:
        print("Creating categories table...")
        Base.metadata.create_all(bind=engine)
        print("Categories table created successfully!")
        
        # 插入默认分类数据
        insert_default_categories()
    else:
        print("Categories table already exists.")
        # 检查是否需要添加新的索引或列
        check_and_update_schema()


def insert_default_categories():
    """
    插入默认分类数据
    为系统创建一些预定义的分类
    """
    db = SessionLocal()
    try:
        default_categories = [
            # 支出分类
            Category(user_id=0, name="餐饮", type=CategoryType.expense, icon="🍔", color="#FF6B6B", is_default=True),
            Category(user_id=0, name="交通", type=CategoryType.expense, icon="🚗", color="#4ECDC4", is_default=True),
            Category(user_id=0, name="购物", type=CategoryType.expense, icon="🛍️", color="#95E1D3", is_default=True),
            Category(user_id=0, name="娱乐", type=CategoryType.expense, icon="🎮", color="#F38181", is_default=True),
            Category(user_id=0, name="医疗", type=CategoryType.expense, icon="💊", color="#AA96DA", is_default=True),
            Category(user_id=0, name="教育", type=CategoryType.expense, icon="📚", color="#FCBAD3", is_default=True),
            Category(user_id=0, name="住房", type=CategoryType.expense, icon="🏠", color="#A8D8EA", is_default=True),
            Category(user_id=0, name="其他", type=CategoryType.expense, icon="📦", color="#C7CEEA", is_default=True),
            
            # 收入分类
            Category(user_id=0, name="工资", type=CategoryType.income, icon="💰", color="#6BCF7F", is_default=True),
            Category(user_id=0, name="奖金", type=CategoryType.income, icon="🎁", color="#FFD93D", is_default=True),
            Category(user_id=0, name="投资", type=CategoryType.income, icon="📈", color="#6BCF7F", is_default=True),
            Category(user_id=0, name="兼职", type=CategoryType.income, icon="💼", color="#95E1D3", is_default=True),
            Category(user_id=0, name="其他", type=CategoryType.income, icon="💵", color="#C7CEEA", is_default=True),
        ]
        
        db.add_all(default_categories)
        db.commit()
        print(f"Inserted {len(default_categories)} default categories.")
    except Exception as e:
        print(f"Error inserting default categories: {e}")
        db.rollback()
    finally:
        db.close()


def check_and_update_schema():
    """
    检查并更新数据库架构
    确保所有索引和约束都已正确创建
    """
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    
    # 检查索引
    indexes = inspector.get_indexes("categories")
    index_names = [idx["name"] for idx in indexes]
    
    required_indexes = ["idx_user_type", "idx_user_default"]
    missing_indexes = [idx for idx in required_indexes if idx not in index_names]
    
    if missing_indexes:
        print(f"Missing indexes: {missing_indexes}")
        print("Recreating table with proper indexes...")
        Base.metadata.create_all(bind=engine)
        print("Schema updated successfully!")
    else:
        print("All indexes are present.")


# 删除所有表（仅用于开发/测试）
def drop_all_tables():
    """
    删除所有表
    警告：此操作将删除所有数据！仅用于开发和测试环境
    """
    confirmation = input("Are you sure you want to drop all tables? This will delete all data! (yes/no): ")
    if confirmation.lower() == "yes":
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped successfully!")
    else:
        print("Operation cancelled.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            init_db()
        elif command == "migrate":
            migrate_database()
        elif command == "drop":
            drop_all_tables()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: init, migrate, drop")
    else:
        print("Usage: python database.py [init|migrate|drop]")
        print("  init    - Initialize database and create all tables")
        print("  migrate - Run database migrations")
        print("  drop    - Drop all tables (WARNING: deletes all data)")