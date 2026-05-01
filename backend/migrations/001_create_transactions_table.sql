-- Migration: Create transactions table with indexes
-- Created: 2024
-- Description: Initial transaction data model with optimized indexes for common queries

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    amount REAL NOT NULL CHECK(amount > 0),
    category_id INTEGER NOT NULL,
    date TEXT NOT NULL,  -- ISO8601 format: YYYY-MM-DD HH:MM:SS
    note TEXT,
    payment_method TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    
    -- Foreign key constraints (enforced if users/categories tables exist)
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- Index for user-based queries (most common access pattern)
CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
    ON transactions(user_id);

-- Composite index for user + date range queries (monthly/yearly reports)
CREATE INDEX IF NOT EXISTS idx_transactions_user_date 
    ON transactions(user_id, date DESC);

-- Index for category analysis queries
CREATE INDEX IF NOT EXISTS idx_transactions_category 
    ON transactions(category_id);

-- Composite index for type-based filtering (income vs expense reports)
CREATE INDEX IF NOT EXISTS idx_transactions_user_type 
    ON transactions(user_id, type);

-- Index for payment method statistics
CREATE INDEX IF NOT EXISTS idx_transactions_payment_method 
    ON transactions(payment_method) 
    WHERE payment_method IS NOT NULL;
