"""Test categories table migration and constraints."""
import pytest
import aiosqlite
import os
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.migration_runner import run_migrations, get_current_version

TEST_DB = "test_categories.db"


@pytest.fixture
async def db():
    """Create test database and run migrations."""
    # Clean up any existing test db
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    # Run migrations
    await run_migrations(TEST_DB)
    
    # Connect and yield
    conn = await aiosqlite.connect(TEST_DB)
    await conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = aiosqlite.Row
    
    yield conn
    
    await conn.close()
    
    # Cleanup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.mark.asyncio
async def test_migration_creates_categories_table(db):
    """Test that migration creates categories table with correct structure."""
    cursor = await db.execute("PRAGMA table_info(categories)")
    columns = await cursor.fetchall()
    
    column_names = [col[1] for col in columns]
    assert "id" in column_names
    assert "user_id" in column_names
    assert "name" in column_names
    assert "type" in column_names
    assert "icon" in column_names
    assert "color" in column_names
    assert "is_default" in column_names
    assert "created_at" in column_names


@pytest.mark.asyncio
async def test_migration_creates_indexes(db):
    """Test that migration creates required indexes."""
    cursor = await db.execute("PRAGMA index_list(categories)")
    indexes = await cursor.fetchall()
    
    index_names = [idx[1] for idx in indexes]
    assert "idx_categories_user_id" in index_names
    assert "idx_categories_user_type" in index_names
    assert "idx_categories_user_type_default" in index_names
    assert "idx_categories_is_default" in index_names


@pytest.mark.asyncio
async def test_type_check_constraint(db):
    """Test that type field only accepts 'income' or 'expense'."""
    # Create a test user first (assuming users table exists)
    try:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)"
        )
        await db.execute("INSERT INTO users (id, username) VALUES (1, 'testuser')")
        await db.commit()
    except:
        pass
    
    # Valid type should work
    await db.execute(
        "INSERT INTO categories (user_id, name, type) VALUES (1, 'Salary', 'income')"
    )
    await db.commit()
    
    # Invalid type should fail
    with pytest.raises(aiosqlite.IntegrityError):
        await db.execute(
            "INSERT INTO categories (user_id, name, type) VALUES (1, 'Invalid', 'other')"
        )
        await db.commit()


@pytest.mark.asyncio
async def test_is_default_check_constraint(db):
    """Test that is_default only accepts 0 or 1."""
    try:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)"
        )
        await db.execute("INSERT INTO users (id, username) VALUES (1, 'testuser')")
        await db.commit()
    except:
        pass
    
    # Valid values should work
    await db.execute(
        "INSERT INTO categories (user_id, name, type, is_default) VALUES (1, 'Cat1', 'income', 0)"
    )
    await db.execute(
        "INSERT INTO categories (user_id, name, type, is_default) VALUES (1, 'Cat2', 'expense', 1)"
    )
    await db.commit()
    
    # Invalid value should fail
    with pytest.raises(aiosqlite.IntegrityError):
        await db.execute(
            "INSERT INTO categories (user_id, name, type, is_default) VALUES (1, 'Cat3', 'income', 2)"
        )
        await db.commit()


@pytest.mark.asyncio
async def test_unique_default_per_user_type(db):
    """Test that only one default category allowed per (user_id, type)."""
    try:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)"
        )
        await db.execute("INSERT INTO users (id, username) VALUES (1, 'testuser')")
        await db.commit()
    except:
        pass
    
    # First default income category should work
    await db.execute(
        "INSERT INTO categories (user_id, name, type, is_default) VALUES (1, 'Default Income', 'income', 1)"
    )
    await db.commit()
    
    # Second default income category for same user should fail
    with pytest.raises(aiosqlite.IntegrityError):
        await db.execute(
            "INSERT INTO categories (user_id, name, type, is_default) VALUES (1, 'Another Default', 'income', 1)"
        )
        await db.commit()
    
    # But default expense category should work (different type)
    await db.execute(
        "INSERT INTO categories (user_id, name, type, is_default) VALUES (1, 'Default Expense', 'expense', 1)"
    )
    await db.commit()


@pytest.mark.asyncio
async def test_foreign_key_cascade_delete(db):
    """Test that deleting user cascades to categories."""
    try:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)"
        )
        await db.execute("INSERT INTO users (id, username) VALUES (1, 'testuser')")
        await db.commit()
    except:
        pass
    
    # Create category
    await db.execute(
        "INSERT INTO categories (user_id, name, type) VALUES (1, 'Test', 'income')"
    )
    await db.commit()
    
    # Verify category exists
    cursor = await db.execute("SELECT COUNT(*) FROM categories WHERE user_id = 1")
    count = (await cursor.fetchone())[0]
    assert count == 1
    
    # Delete user
    await db.execute("DELETE FROM users WHERE id = 1")
    await db.commit()
    
    # Category should be deleted too
    cursor = await db.execute("SELECT COUNT(*) FROM categories WHERE user_id = 1")
    count = (await cursor.fetchone())[0]
    assert count == 0


@pytest.mark.asyncio
async def test_migration_version_tracking(db):
    """Test that migration version is tracked correctly."""
    version = await get_current_version(db)
    assert version >= 1  # Should have at least version 1 (categories migration)
    
    # Check migration record exists
    cursor = await db.execute(
        "SELECT version, description FROM schema_migrations WHERE version = 1"
    )
    row = await cursor.fetchone()
    assert row is not None
    assert "categories" in row[1].lower()
