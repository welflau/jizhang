import pytest
from sqlalchemy import inspect, Index
from backend.app.models.category import Category
from backend.app.core.database import Base, engine


class TestCategoryMigration:
    """测试 Category 表结构和迁移"""

    def test_category_table_exists(self):
        """测试 categories 表是否存在"""
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert 'categories' in tables, "categories 表不存在"

    def test_category_table_columns(self):
        """测试 categories 表的列结构"""
        inspector = inspect(engine)
        columns = inspector.get_columns('categories')
        column_names = [col['name'] for col in columns]
        
        # 验证必需的列存在
        required_columns = ['id', 'user_id', 'name', 'type', 'icon', 'color', 'is_default']
        for col in required_columns:
            assert col in column_names, f"列 {col} 不存在"

    def test_category_column_types(self):
        """测试 categories 表的列类型"""
        inspector = inspect(engine)
        columns = {col['name']: col for col in inspector.get_columns('categories')}
        
        # 验证 id 列
        assert columns['id']['primary_key'] == 1 or columns['id']['autoincrement'], "id 应该是主键且自增"
        
        # 验证 user_id 列
        assert not columns['user_id']['nullable'], "user_id 不应该为空"
        
        # 验证 name 列
        assert not columns['name']['nullable'], "name 不应该为空"
        
        # 验证 type 列
        assert not columns['type']['nullable'], "type 不应该为空"
        
        # 验证 is_default 列
        assert not columns['is_default']['nullable'], "is_default 不应该为空"

    def test_category_foreign_keys(self):
        """测试 categories 表的外键约束"""
        inspector = inspect(engine)
        foreign_keys = inspector.get_foreign_keys('categories')
        
        # 验证 user_id 外键
        user_fk = [fk for fk in foreign_keys if 'user_id' in fk['constrained_columns']]
        assert len(user_fk) > 0, "user_id 应该有外键约束"
        assert user_fk[0]['referred_table'] == 'users', "user_id 应该引用 users 表"

    def test_category_indexes(self):
        """测试 categories 表的索引"""
        inspector = inspect(engine)
        indexes = inspector.get_indexes('categories')
        index_columns = [idx['column_names'] for idx in indexes]
        
        # 验证 user_id 索引
        assert any('user_id' in cols for cols in index_columns), "应该有 user_id 索引"
        
        # 验证复合索引 (user_id, type)
        assert any(set(['user_id', 'type']).issubset(set(cols)) for cols in index_columns), \
            "应该有 (user_id, type) 复合索引"

    def test_category_unique_constraints(self):
        """测试 categories 表的唯一约束"""
        inspector = inspect(engine)
        unique_constraints = inspector.get_unique_constraints('categories')
        
        # 验证 (user_id, name) 唯一约束
        constraint_columns = [set(uc['column_names']) for uc in unique_constraints]
        assert any({'user_id', 'name'}.issubset(cols) for cols in constraint_columns), \
            "应该有 (user_id, name) 唯一约束"

    def test_category_check_constraints(self):
        """测试 categories 表的检查约束"""
        inspector = inspect(engine)
        
        # 注意：SQLite 不完全支持检查约束的反射，这里主要测试模型定义
        # 验证 type 字段只能是 'income' 或 'expense'
        # 这个测试通过尝试插入无效数据来验证
        pass  # 在实际插入测试中验证

    def test_create_category_with_valid_type(self, db_session, test_user):
        """测试创建有效类型的分类"""
        category = Category(
            user_id=test_user.id,
            name="测试分类",
            type="income",
            icon="💰",
            color="#FF5733",
            is_default=False
        )
        db_session.add(category)
        db_session.commit()
        
        assert category.id is not None
        assert category.type == "income"

    def test_create_category_with_invalid_type(self, db_session, test_user):
        """测试创建无效类型的分类应该失败"""
        category = Category(
            user_id=test_user.id,
            name="测试分类",
            type="invalid_type",
            icon="💰",
            color="#FF5733",
            is_default=False
        )
        db_session.add(category)
        
        with pytest.raises(Exception):  # 应该抛出数据库约束错误
            db_session.commit()
        
        db_session.rollback()

    def test_category_default_values(self, db_session, test_user):
        """测试分类的默认值"""
        category = Category(
            user_id=test_user.id,
            name="测试分类",
            type="expense"
        )
        db_session.add(category)
        db_session.commit()
        
        # 验证默认值
        assert category.is_default is False
        assert category.icon is not None or category.icon == ""
        assert category.color is not None or category.color == ""

    def test_category_name_uniqueness_per_user(self, db_session, test_user, test_user2):
        """测试同一用户不能有重名分类，但不同用户可以"""
        # 创建第一个分类
        category1 = Category(
            user_id=test_user.id,
            name="餐饮",
            type="expense",
            icon="🍔",
            color="#FF5733",
            is_default=False
        )
        db_session.add(category1)
        db_session.commit()
        
        # 同一用户创建重名分类应该失败
        category2 = Category(
            user_id=test_user.id,
            name="餐饮",
            type="expense",
            icon="🍕",
            color="#33FF57",
            is_default=False
        )
        db_session.add(category2)
        
        with pytest.raises(Exception):  # 应该抛出唯一约束错误
            db_session.commit()
        
        db_session.rollback()
        
        # 不同用户创建同名分类应该成功
        category3 = Category(
            user_id=test_user2.id,
            name="餐饮",
            type="expense",
            icon="🍔",
            color="#FF5733",
            is_default=False
        )
        db_session.add(category3)
        db_session.commit()
        
        assert category3.id is not None

    def test_category_cascade_delete(self, db_session, test_user):
        """测试删除用户时级联删除分类"""
        # 创建分类
        category = Category(
            user_id=test_user.id,
            name="测试分类",
            type="income",
            icon="💰",
            color="#FF5733",
            is_default=False
        )
        db_session.add(category)
        db_session.commit()
        
        category_id = category.id
        
        # 删除用户
        db_session.delete(test_user)
        db_session.commit()
        
        # 验证分类也被删除
        deleted_category = db_session.query(Category).filter_by(id=category_id).first()
        assert deleted_category is None, "删除用户后，关联的分类应该被级联删除"

    def test_query_performance_with_indexes(self, db_session, test_user):
        """测试索引对查询性能的影响"""
        # 创建多个分类
        for i in range(100):
            category = Category(
                user_id=test_user.id,
                name=f"分类{i}",
                type="income" if i % 2 == 0 else "expense",
                icon="💰",
                color="#FF5733",
                is_default=False
            )
            db_session.add(category)
        db_session.commit()
        
        # 测试按 user_id 查询
        import time
        start_time = time.time()
        categories = db_session.query(Category).filter_by(user_id=test_user.id).all()
        query_time = time.time() - start_time
        
        assert len(categories) == 100
        assert query_time < 1.0, "查询时间应该小于1秒（有索引的情况下）"
        
        # 测试按 user_id 和 type 查询
        start_time = time.time()
        income_categories = db_session.query(Category).filter_by(
            user_id=test_user.id,
            type="income"
        ).all()
        query_time = time.time() - start_time
        
        assert len(income_categories) == 50
        assert query_time < 1.0, "复合索引查询时间应该小于1秒"

    def test_migration_rollback(self):
        """测试迁移回滚功能"""
        # 这个测试需要配合实际的迁移脚本
        # 验证可以安全地回滚迁移
        pass  # 在集成测试中实现

    def test_category_timestamps(self, db_session, test_user):
        """测试分类的时间戳字段"""
        category = Category(
            user_id=test_user.id,
            name="测试分类",
            type="income",
            icon="💰",
            color="#FF5733",
            is_default=False
        )
        db_session.add(category)
        db_session.commit()
        
        # 验证创建时间和更新时间
        assert hasattr(category, 'created_at') or hasattr(category, 'created_time')
        assert hasattr(category, 'updated_at') or hasattr(category, 'updated_time')
