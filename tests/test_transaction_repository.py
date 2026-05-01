"""Unit tests for transaction repository."""
import pytest
import aiosqlite
from datetime import datetime, timedelta
from backend.models.transaction import TransactionCreate, TransactionUpdate
from backend.repositories.transaction_repository import TransactionRepository
import os
import tempfile


@pytest.fixture
async def test_db():
    """Create a temporary test database."""
    # Create temp db file
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row
    
    # Create schema
    await conn.execute("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            amount REAL NOT NULL CHECK(amount > 0),
            category_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            note TEXT,
            payment_method TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    await conn.commit()
    
    yield conn
    
    await conn.close()
    os.unlink(db_path)


@pytest.mark.asyncio
async def test_create_transaction(test_db):
    """Test creating a new transaction."""
    data = TransactionCreate(
        type="expense",
        amount=99.99,
        category_id=1,
        date=datetime.now(),
        note="Test expense",
        payment_method="card"
    )
    
    result = await TransactionRepository.create(test_db, user_id=1, data=data)
    
    assert result.id > 0
    assert result.user_id == 1
    assert result.type == "expense"
    assert result.amount == 99.99
    assert result.note == "Test expense"


@pytest.mark.asyncio
async def test_get_by_id(test_db):
    """Test retrieving transaction by ID."""
    # Create a transaction first
    data = TransactionCreate(
        type="income",
        amount=500.0,
        category_id=2,
        date=datetime.now(),
        note="Salary"
    )
    created = await TransactionRepository.create(test_db, user_id=1, data=data)
    
    # Retrieve it
    result = await TransactionRepository.get_by_id(test_db, created.id, user_id=1)
    
    assert result is not None
    assert result.id == created.id
    assert result.amount == 500.0
    
    # Test with wrong user_id
    result = await TransactionRepository.get_by_id(test_db, created.id, user_id=999)
    assert result is None


@pytest.mark.asyncio
async def test_list_by_user_with_filters(test_db):
    """Test listing transactions with filters."""
    user_id = 1
    now = datetime.now()
    
    # Create multiple transactions
    await TransactionRepository.create(test_db, user_id, TransactionCreate(
        type="expense", amount=100, category_id=1, date=now - timedelta(days=5)
    ))
    await TransactionRepository.create(test_db, user_id, TransactionCreate(
        type="income", amount=200, category_id=2, date=now - timedelta(days=3)
    ))
    await TransactionRepository.create(test_db, user_id, TransactionCreate(
        type="expense", amount=50, category_id=1, date=now - timedelta(days=1)
    ))
    
    # Test: get all
    all_transactions = await TransactionRepository.list_by_user(test_db, user_id)
    assert len(all_transactions) == 3
    
    # Test: filter by type
    expenses = await TransactionRepository.list_by_user(test_db, user_id, transaction_type="expense")
    assert len(expenses) == 2
    
    # Test: filter by date range
    recent = await TransactionRepository.list_by_user(
        test_db, user_id,
        start_date=now - timedelta(days=2)
    )
    assert len(recent) == 1


@pytest.mark.asyncio
async def test_update_transaction(test_db):
    """Test updating transaction fields."""
    # Create initial transaction
    data = TransactionCreate(
        type="expense",
        amount=100,
        category_id=1,
        date=datetime.now(),
        note="Original note"
    )
    created = await TransactionRepository.create(test_db, user_id=1, data=data)
    
    # Update some fields
    update_data = TransactionUpdate(
        amount=150.0,
        note="Updated note"
    )
    updated = await TransactionRepository.update(test_db, created.id, user_id=1, data=update_data)
    
    assert updated is not None
    assert updated.amount == 150.0
    assert updated.note == "Updated note"
    assert updated.type == "expense"  # Unchanged field


@pytest.mark.asyncio
async def test_delete_transaction(test_db):
    """Test deleting a transaction."""
    # Create a transaction
    data = TransactionCreate(
        type="expense",
        amount=100,
        category_id=1,
        date=datetime.now()
    )
    created = await TransactionRepository.create(test_db, user_id=1, data=data)
    
    # Delete it
    deleted = await TransactionRepository.delete(test_db, created.id, user_id=1)
    assert deleted is True
    
    # Verify it's gone
    result = await TransactionRepository.get_by_id(test_db, created.id, user_id=1)
    assert result is None
    
    # Try deleting non-existent
    deleted = await TransactionRepository.delete(test_db, 99999, user_id=1)
    assert deleted is False
