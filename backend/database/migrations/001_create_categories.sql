-- Migration: Create categories table
-- Version: 001
-- Description: Creates categories table with proper constraints and indexes
-- Business rules:
--   1. Each category belongs to a user (foreign key to users table)
--   2. Type must be either 'income' or 'expense' (CHECK constraint)
--   3. Each user can have only ONE default category per type (partial unique index)
--   4. Deleting a user cascades to their categories

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    icon TEXT,
    color TEXT,
    is_default INTEGER NOT NULL DEFAULT 0 CHECK(is_default IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Index for querying categories by user
CREATE INDEX IF NOT EXISTS idx_categories_user_id 
ON categories(user_id);

-- Composite index for filtering by user and type (most common query pattern)
CREATE INDEX IF NOT EXISTS idx_categories_user_type 
ON categories(user_id, type);

-- Partial unique index: only ONE default category per (user_id, type) combination
-- SQLite partial indexes only enforce uniqueness where the WHERE clause is true
CREATE UNIQUE INDEX IF NOT EXISTS idx_categories_user_type_default 
ON categories(user_id, type) 
WHERE is_default = 1;

-- Index for quickly finding default categories
CREATE INDEX IF NOT EXISTS idx_categories_is_default 
ON categories(user_id, is_default) 
WHERE is_default = 1;
