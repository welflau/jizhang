"""Database schema definitions as Python constants.

Provides reference DDL statements for documentation and validation purposes.
Actual schema is managed through SQL migration files.
"""

# Categories table DDL for reference
CATEGORIES_TABLE_DDL = """
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    icon TEXT,
    color TEXT,
    is_default INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, name)
);
"""

# Index definitions for categories table
CATEGORIES_INDEXES = [
    "CREATE INDEX idx_categories_user_id ON categories(user_id)",
    "CREATE INDEX idx_categories_user_type ON categories(user_id, type)",
    "CREATE INDEX idx_categories_is_default ON categories(is_default) WHERE is_default = 1",
]

# Field constraints documentation
CATEGORIES_CONSTRAINTS = {
    "type": "Must be 'income' or 'expense'",
    "is_default": "Boolean flag (0 or 1), defaults to 0",
    "user_id": "Foreign key to users.id with CASCADE delete",
    "name": "Unique per user (composite unique constraint with user_id)",
}
