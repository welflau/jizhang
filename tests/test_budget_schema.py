tests/test_budget_schema.py

import pytest
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.models.budget import Budget
from app.models.user import User
from app.models.category import Category
from app.database import Base


@pytest.fixture
def engine():
    """Create test database engine"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create test database session"""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestBudgetSchema:
    """Test budget table schema"""

    def test_budget_table_exists(self, engine):
        """Test that budgets table exists"""
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert 'budgets' in tables

    def test_budget_columns(self, engine):
        """Test that budgets table has all required columns"""
        inspector = inspect(engine)
        columns = {col['name']: col for col in inspector.get_columns('budgets')}
        
        # Check all required columns exist
        assert 'id' in columns
        assert 'user_id' in columns
        assert 'category_id' in columns
        assert 'amount' in columns
        assert 'period' in columns
        assert 'created_at' in columns

    def test_budget_primary_key(self, engine):
        """Test that id is the primary key"""
        inspector = inspect(engine)
        pk_constraint = inspector.get_pk_constraint('budgets')
        assert 'id' in pk_constraint['constrained_columns']

    def test_budget_foreign_keys(self, engine):
        """Test foreign key constraints"""
        inspector = inspect(engine)
        foreign_keys = inspector.get_foreign_keys('budgets')
        
        fk_columns = [fk['constrained_columns'][0] for fk in foreign_keys]
        
        # Check user_id foreign key
        assert 'user_id' in fk_columns
        
        # Check category_id foreign key
        assert 'category_id' in fk_columns
        
        # Verify referenced tables
        for fk in foreign_keys:
            if fk['constrained_columns'][0] == 'user_id':
                assert fk['referred_table'] == 'users'
            if fk['constrained_columns'][0] == 'category_id':
                assert fk['referred_table'] == 'categories'

    def test_budget_indexes(self, engine):
        """Test that required indexes exist"""
        inspector = inspect(engine)
        indexes = inspector.get_indexes('budgets')
        
        index_columns = []
        for idx in indexes:
            index_columns.extend(idx['column_names'])
        
        # Check user_id index
        assert 'user_id' in index_columns
        
        # Check period index
        assert 'period' in index_columns

    def test_budget_nullable_constraints(self, engine):
        """Test nullable constraints on columns"""
        inspector = inspect(engine)
        columns = {col['name']: col for col in inspector.get_columns('budgets')}
        
        # Required fields should not be nullable
        assert columns['id']['nullable'] is False
        assert columns['user_id']['nullable'] is False
        assert columns['amount']['nullable'] is False
        assert columns['period']['nullable'] is False
        assert columns['created_at']['nullable'] is False
        
        # category_id should be nullable (optional)
        assert columns['category_id']['nullable'] is True

    def test_create_budget_with_all_fields(self, session):
        """Test creating a budget with all fields"""
        # Create test user
        user = User(username='testuser', email='test@example.com', password_hash='hash')
        session.add(user)
        session.flush()
        
        # Create test category
        category = Category(name='Food', user_id=user.id)
        session.add(category)
        session.flush()
        
        # Create budget
        budget = Budget(
            user_id=user.id,
            category_id=category.id,
            amount=1000.00,
            period='2024-01',
            created_at=datetime.utcnow()
        )
        session.add(budget)
        session.commit()
        
        # Verify budget was created
        assert budget.id is not None
        assert budget.user_id == user.id
        assert budget.category_id == category.id
        assert budget.amount == 1000.00
        assert budget.period == '2024-01'
        assert budget.created_at is not None

    def test_create_budget_without_category(self, session):
        """Test creating a budget without category (category_id is optional)"""
        # Create test user
        user = User(username='testuser', email='test@example.com', password_hash='hash')
        session.add(user)
        session.flush()
        
        # Create budget without category
        budget = Budget(
            user_id=user.id,
            category_id=None,
            amount=2000.00,
            period='2024-02',
            created_at=datetime.utcnow()
        )
        session.add(budget)
        session.commit()
        
        # Verify budget was created
        assert budget.id is not None
        assert budget.user_id == user.id
        assert budget.category_id is None
        assert budget.amount == 2000.00
        assert budget.period == '2024-02'

    def test_budget_period_format(self, session):
        """Test that period follows YYYY-MM format"""
        user = User(username='testuser', email='test@example.com', password_hash='hash')
        session.add(user)
        session.flush()
        
        # Valid period format
        budget = Budget(
            user_id=user.id,
            amount=1500.00,
            period='2024-03',
            created_at=datetime.utcnow()
        )
        session.add(budget)
        session.commit()
        
        assert budget.period == '2024-03'
        assert len(budget.period) == 7
        assert budget.period[4] == '-'

    def test_budget_amount_precision(self, session):
        """Test that amount field handles decimal values correctly"""
        user = User(username='testuser', email='test@example.com', password_hash='hash')
        session.add(user)
        session.flush()
        
        budget = Budget(
            user_id=user.id,
            amount=1234.56,
            period='2024-04',
            created_at=datetime.utcnow()
        )
        session.add(budget)
        session.commit()
        
        # Retrieve and verify precision
        retrieved_budget = session.query(Budget).filter_by(id=budget.id).first()
        assert float(retrieved_budget.amount) == 1234.56

    def test_budget_user_relationship(self, session):
        """Test relationship between budget and user"""
        user = User(username='testuser', email='test@example.com', password_hash='hash')
        session.add(user)
        session.flush()
        
        budget = Budget(
            user_id=user.id,
            amount=3000.00,
            period='2024-05',
            created_at=datetime.utcnow()
        )
        session.add(budget)
        session.commit()
        
        # Test relationship
        assert budget.user == user
        assert budget in user.budgets

    def test_budget_category_relationship(self, session):
        """Test relationship between budget and category"""
        user = User(username='testuser', email='test@example.com', password_hash='hash')
        session.add(user)
        session.flush()
        
        category = Category(name='Transport', user_id=user.id)
        session.add(category)
        session.flush()
        
        budget = Budget(
            user_id=user.id,
            category_id=category.id,
            amount=500.00,
            period='2024-06',
            created_at=datetime.utcnow()
        )
        session.add(budget)
        session.commit()
        
        # Test relationship
        assert budget.category == category
        assert budget in category.budgets

    def test_multiple_budgets_same_user(self, session):
        """Test creating multiple budgets for the same user"""
        user = User(username='testuser', email='test@example.com', password_hash='hash')
        session.add(user)
        session.flush()
        
        budget1 = Budget(user_id=user.id, amount=1000.00, period='2024-01', created_at=datetime.utcnow())
        budget2 = Budget(user_id=user.id, amount=1500.00, period='2024-02', created_at=datetime.utcnow())
        
        session.add_all([budget1, budget2])
        session.commit()
        
        user_budgets = session.query(Budget).filter_by(user_id=user.id).all()
        assert len(user_budgets) == 2

    def test_query_performance_with_indexes(self, session):
        """Test that queries using indexed columns perform efficiently"""
        # Create test data
        user = User(username='testuser', email='test@example.com', password_hash='hash')
        session.add(user)
        session.flush()
        
        # Create multiple budgets
        for i in range(10):
            budget = Budget(
                user_id=user.id,
                amount=1000.00 * (i + 1),
                period=f'2024-{str(i+1).zfill(2)}',
                created_at=datetime.utcnow()
            )
            session.add(budget)
        session.commit()
        
        # Query by user_id (indexed)
        budgets_by_user = session.query(Budget).filter_by(user_id=user.id).all()
        assert len(budgets_by_user) == 10
        
        # Query by period (indexed)
        budgets_by_period = session.query(Budget).filter_by(period='2024-05').all()
        assert len(budgets_by_period) == 1
        
        # Combined query
        budget = session.query(Budget).filter_by(user_id=user.id, period='2024-03').first()
        assert budget is not None
        assert budget.amount == 3000.00