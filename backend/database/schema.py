"""Database schema definitions for reference.

These constants document the expected table structures.
Actual tables are created via migration scripts.
"""

# Categories table DDL (for reference only - created by migration)
CATEGORIES_TABLE_DDL = """
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    icon TEXT,
    color TEXT,
    is_default INTEGER NOT NULL DEFAULT 0 CHECK(is_default IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
)
"""

# Categories indexes (for reference)
CATEGORIES_INDEXES = [
    "CREATE INDEX idx_categories_user_id ON categories(user_id)",
    "CREATE INDEX idx_categories_user_type ON categories(user_id, type)",
    "CREATE UNIQUE INDEX idx_categories_user_type_default ON categories(user_id, type) WHERE is_default = 1",
    "CREATE INDEX idx_categories_is_default ON categories(user_id, is_default) WHERE is_default = 1",
]

# Field constraints documentation
CATEGORIES_CONSTRAINTS = {
    "type": "Must be 'income' or 'expense'",
    "is_default": "Boolean (0 or 1). Only one default category allowed per (user_id, type)",
    "user_id": "Foreign key to users.id with CASCADE delete",
}
