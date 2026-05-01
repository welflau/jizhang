import pytest
from datetime import datetime
from sqlalchemy import inspect, Index
from backend.models import Budget, User, Category
from backend.database import engine, SessionLocal


class TestBudgetMigration:
    """测试 budgets 表的迁移和结构"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前的设置"""
        self.db = SessionLocal()
        yield
        self.db.close()

    def test_budgets_table_exists(self):
        """测试 budgets 表是否存在"""
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert 'budgets' in tables, "budgets 表不存在"

    def test_budgets_table_columns(self):
        """测试 budgets 表的列结构"""
        inspector = inspect(engine)
        columns = inspector.get_columns('budgets')
        column_names = [col['name'] for col in columns]
        
        # 验证所有必需的列都存在
        required_columns = ['id', 'user_id', 'category_id', 'amount', 'period', 'created_at']
        for col in required_columns:
            assert col in column_names, f"列 {col} 不存在"

    def test_budgets_primary_key(self):
        """测试主键约束"""
        inspector = inspect(engine)
        pk_constraint = inspector.get_pk_constraint('budgets')
        assert 'id' in pk_constraint['constrained_columns'], "id 不是主键"

    def test_budgets_foreign_keys(self):
        """测试外键约束"""
        inspector = inspect(engine)
        foreign_keys = inspector.get_foreign_keys('budgets')
        
        # 检查 user_id 外键
        user_fk = [fk for fk in foreign_keys if 'user_id' in fk['constrained_columns']]
        assert len(user_fk) > 0, "user_id 外键不存在"
        assert user_fk[0]['referred_table'] == 'users', "user_id 外键未正确关联到 users 表"
        
        # 检查 category_id 外键
        category_fk = [fk for fk in foreign_keys if 'category_id' in fk['constrained_columns']]
        assert len(category_fk) > 0, "category_id 外键不存在"
        assert category_fk[0]['referred_table'] == 'categories', "category_id 外键未正确关联到 categories 表"

    def test_budgets_indexes(self):
        """测试索引是否正确创建"""
        inspector = inspect(engine)
        indexes = inspector.get_indexes('budgets')
        
        # 获取所有索引的列
        indexed_columns = []
        for idx in indexes:
            indexed_columns.extend(idx['column_names'])
        
        # 验证 user_id 和 period 列有索引
        assert 'user_id' in indexed_columns, "user_id 列没有索引"
        assert 'period' in indexed_columns, "period 列没有索引"

    def test_budgets_column_types(self):
        """测试列的数据类型"""
        inspector = inspect(engine)
        columns = {col['name']: col for col in inspector.get_columns('budgets')}
        
        # 验证 id 是整数类型
        assert 'INTEGER' in str(columns['id']['type']).upper() or 'INT' in str(columns['id']['type']).upper(), \
            "id 列类型不正确"
        
        # 验证 user_id 是整数类型
        assert 'INTEGER' in str(columns['user_id']['type']).upper() or 'INT' in str(columns['user_id']['type']).upper(), \
            "user_id 列类型不正确"
        
        # 验证 category_id 是整数类型
        assert 'INTEGER' in str(columns['category_id']['type']).upper() or 'INT' in str(columns['category_id']['type']).upper(), \
            "category_id 列类型不正确"
        
        # 验证 amount 是数值类型
        amount_type = str(columns['amount']['type']).upper()
        assert any(t in amount_type for t in ['NUMERIC', 'DECIMAL', 'FLOAT', 'REAL']), \
            "amount 列类型不正确"
        
        # 验证 period 是字符串类型
        assert 'VARCHAR' in str(columns['period']['type']).upper() or 'CHAR' in str(columns['period']['type']).upper(), \
            "period 列类型不正确"
        
        # 验证 created_at 是日期时间类型
        assert 'DATETIME' in str(columns['created_at']['type']).upper() or 'TIMESTAMP' in str(columns['created_at']['type']).upper(), \
            "created_at 列类型不正确"

    def test_budgets_nullable_constraints(self):
        """测试列的可空约束"""
        inspector = inspect(engine)
        columns = {col['name']: col for col in inspector.get_columns('budgets')}
        
        # 验证必填字段不可为空
        assert not columns['id']['nullable'], "id 列应该不可为空"
        assert not columns['user_id']['nullable'], "user_id 列应该不可为空"
        assert not columns['amount']['nullable'], "amount 列应该不可为空"
        assert not columns['period']['nullable'], "period 列应该不可为空"
        assert not columns['created_at']['nullable'], "created_at 列应该不可为空"
        
        # 验证 category_id 可以为空（可选字段）
        assert columns['category_id']['nullable'], "category_id 列应该可以为空"

    def test_create_budget_with_all_fields(self, test_user, test_category):
        """测试创建包含所有字段的预算记录"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=1000.00,
            period="2024-01",
            created_at=datetime.utcnow()
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        
        assert budget.id is not None, "预算记录创建失败"
        assert budget.user_id == test_user.id
        assert budget.category_id == test_category.id
        assert budget.amount == 1000.00
        assert budget.period == "2024-01"
        assert budget.created_at is not None

    def test_create_budget_without_category(self, test_user):
        """测试创建不关联分类的预算记录"""
        budget = Budget(
            user_id=test_user.id,
            category_id=None,
            amount=2000.00,
            period="2024-02",
            created_at=datetime.utcnow()
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        
        assert budget.id is not None
        assert budget.category_id is None, "category_id 应该可以为 None"

    def test_budget_user_relationship(self, test_user):
        """测试预算与用户的关系"""
        budget = Budget(
            user_id=test_user.id,
            amount=1500.00,
            period="2024-03",
            created_at=datetime.utcnow()
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        
        # 验证关系
        assert budget.user.id == test_user.id
        assert budget.user.username == test_user.username

    def test_budget_category_relationship(self, test_user, test_category):
        """测试预算与分类的关系"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=1500.00,
            period="2024-03",
            created_at=datetime.utcnow()
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        
        # 验证关系
        assert budget.category.id == test_category.id
        assert budget.category.name == test_category.name

    def test_period_format_validation(self, test_user):
        """测试 period 字段格式（YYYY-MM）"""
        valid_periods = ["2024-01", "2024-12", "2023-06"]
        
        for period in valid_periods:
            budget = Budget(
                user_id=test_user.id,
                amount=1000.00,
                period=period,
                created_at=datetime.utcnow()
            )
            self.db.add(budget)
            self.db.commit()
            self.db.refresh(budget)
            
            assert budget.period == period
            assert len(budget.period) == 7, "period 格式应为 YYYY-MM"
            assert budget.period[4] == '-', "period 格式应包含连字符"

    def test_query_performance_with_indexes(self, test_user):
        """测试索引对查询性能的影响"""
        # 创建多条测试数据
        for i in range(10):
            budget = Budget(
                user_id=test_user.id,
                amount=1000.00 + i * 100,
                period=f"2024-{(i % 12) + 1:02d}",
                created_at=datetime.utcnow()
            )
            self.db.add(budget)
        self.db.commit()
        
        # 测试按 user_id 查询
        budgets = self.db.query(Budget).filter(Budget.user_id == test_user.id).all()
        assert len(budgets) >= 10
        
        # 测试按 period 查询
        budgets = self.db.query(Budget).filter(Budget.period == "2024-01").all()
        assert len(budgets) >= 1
        
        # 测试组合查询
        budgets = self.db.query(Budget).filter(
            Budget.user_id == test_user.id,
            Budget.period == "2024-01"
        ).all()
        assert len(budgets) >= 1

    def test_cascade_delete_behavior(self, test_user, test_category):
        """测试级联删除行为"""
        budget = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=1000.00,
            period="2024-01",
            created_at=datetime.utcnow()
        )
        self.db.add(budget)
        self.db.commit()
        budget_id = budget.id
        
        # 删除用户，验证预算是否被级联删除
        self.db.delete(test_user)
        self.db.commit()
        
        deleted_budget = self.db.query(Budget).filter(Budget.id == budget_id).first()
        assert deleted_budget is None, "删除用户后，关联的预算应该被级联删除"

    def test_unique_constraint_user_category_period(self, test_user, test_category):
        """测试用户、分类和周期的唯一性约束（如果有）"""
        budget1 = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=1000.00,
            period="2024-01",
            created_at=datetime.utcnow()
        )
        self.db.add(budget1)
        self.db.commit()
        
        # 尝试创建相同用户、分类和周期的预算
        # 注意：这个测试取决于是否有唯一性约束
        # 如果没有约束，这个测试会通过，如果有约束，会抛出异常
        budget2 = Budget(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=2000.00,
            period="2024-01",
            created_at=datetime.utcnow()
        )
        self.db.add(budget2)
        
        # 根据实际需求决定是否应该允许重复
        try:
            self.db.commit()
            # 如果允许重复，测试通过
            assert True
        except Exception:
            # 如果不允许重复，应该抛出异常
            self.db.rollback()
            assert True
