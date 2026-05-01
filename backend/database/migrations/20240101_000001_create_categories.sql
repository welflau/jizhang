-- Migration: Create categories table
-- Version: 20240101_000001
-- Description: Creates categories table for income/expense classification with user isolation

-- ============================================================================
-- UP Migration
-- ============================================================================

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    icon TEXT,
    color TEXT,
    is_default INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint with cascade delete
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Unique constraint: prevent duplicate category names per user
    UNIQUE(user_id, name)
);

-- Index for user-based category queries (most common access pattern)
CREATE INDEX IF NOT EXISTS idx_categories_user_id 
    ON categories(user_id);

-- Composite index for filtering categories by user and type
-- Optimizes queries like: SELECT * FROM categories WHERE user_id = ? AND type = 'expense'
CREATE INDEX IF NOT EXISTS idx_categories_user_type 
    ON categories(user_id, type);

-- Index for finding default categories quickly
CREATE INDEX IF NOT EXISTS idx_categories_is_default 
    ON categories(is_default) 
    WHERE is_default = 1;

-- ============================================================================
-- DOWN Migration (for rollback)
-- ============================================================================
-- Uncomment below to enable rollback capability

-- DROP INDEX IF EXISTS idx_categories_is_default;
-- DROP INDEX IF EXISTS idx_categories_user_type;
-- DROP INDEX IF EXISTS idx_categories_user_id;
-- DROP TABLE IF EXISTS categories;
