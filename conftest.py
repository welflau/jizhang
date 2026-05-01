# conftest.py
import pytest
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app
from models import db, User, Category, Transaction
from datetime import datetime


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        # Clear all tables before each test
        db.session.query(Transaction).delete()
        db.session.query(Category).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        yield db.session
        
        # Cleanup after test
        db.session.rollback()


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        username='testuser',
        email='test@example.com'
    )
    user.set_password('testpassword123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user"""
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpassword123'
    })
    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def income_categories(db_session, test_user):
    """Create test income categories"""
    categories = [
        Category(name='工资', type='income', user_id=test_user.id),
        Category(name='奖金', type='income', user_id=test_user.id),
        Category(name='投资收益', type='income', user_id=test_user.id)
    ]
    for cat in categories:
        db_session.add(cat)
    db_session.commit()
    return categories


@pytest.fixture
def expense_categories(db_session, test_user):
    """Create test expense categories"""
    categories = [
        Category(name='餐饮', type='expense', user_id=test_user.id),
        Category(name='交通', type='expense', user_id=test_user.id),
        Category(name='购物', type='expense', user_id=test_user.id)
    ]
    for cat in categories:
        db_session.add(cat)
    db_session.commit()
    return categories


@pytest.fixture
def all_categories(income_categories, expense_categories):
    """Get all test categories"""
    return income_categories + expense_categories


@pytest.fixture
def test_transactions(db_session, test_user, all_categories):
    """Create test transactions"""
    transactions = [
        Transaction(
            amount=5000.00,
            type='income',
            category_id=all_categories[0].id,
            user_id=test_user.id,
            date=datetime(2024, 1, 15),
            description='月工资'
        ),
        Transaction(
            amount=200.50,
            type='expense',
            category_id=all_categories[3].id,
            user_id=test_user.id,
            date=datetime(2024, 1, 16),
            description='午餐'
        ),
        Transaction(
            amount=50.00,
            type='expense',
            category_id=all_categories[4].id,
            user_id=test_user.id,
            date=datetime(2024, 1, 17),
            description='地铁卡充值'
        )
    ]
    for trans in transactions:
        db_session.add(trans)
    db_session.commit()
    return transactions


@pytest.fixture
def second_user(db_session):
    """Create a second test user"""
    user = User(
        username='testuser2',
        email='test2@example.com'
    )
    user.set_password('testpassword456')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def second_user_headers(client, second_user):
    """Get authentication headers for second test user"""
    response = client.post('/api/auth/login', json={
        'username': 'testuser2',
        'password': 'testpassword456'
    })
    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def category_with_transactions(db_session, test_user):
    """Create a category with associated transactions"""
    category = Category(name='测试分类', type='expense', user_id=test_user.id)
    db_session.add(category)
    db_session.commit()
    
    transaction = Transaction(
        amount=100.00,
        type='expense',
        category_id=category.id,
        user_id=test_user.id,
        date=datetime.now(),
        description='测试交易'
    )
    db_session.add(transaction)
    db_session.commit()
    
    return category


@pytest.fixture
def empty_category(db_session, test_user):
    """Create a category without transactions"""
    category = Category(name='空分类', type='expense', user_id=test_user.id)
    db_session.add(category)
    db_session.commit()
    return category