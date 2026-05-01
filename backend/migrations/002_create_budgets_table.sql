-- Migration: Create budgets table
-- Description: Add budgets table with user_id, category_id, amount, period, and timestamps
-- Author: DevAgent
-- Date: 2024

-- Create budgets table
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER,
    amount DECIMAL(10, 2) NOT NULL CHECK(amount >= 0),
    period VARCHAR(7) NOT NULL CHECK(period GLOB '[0-9][0-9][0-9][0-9]-[0-1][0-9]'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Create index on user_id for faster user-specific queries
CREATE INDEX IF NOT EXISTS idx_budgets_user_id ON budgets(user_id);

-- Create index on period for faster period-based queries
CREATE INDEX IF NOT EXISTS idx_budgets_period ON budgets(period);

-- Create composite index on user_id and period for optimal query performance
CREATE INDEX IF NOT EXISTS idx_budgets_user_period ON budgets(user_id, period);

-- Create index on category_id for category-based filtering
CREATE INDEX IF NOT EXISTS idx_budgets_category_id ON budgets(category_id);

-- Create unique constraint to prevent duplicate budgets for same user, category, and period
CREATE UNIQUE INDEX IF NOT EXISTS idx_budgets_unique_user_category_period 
    ON budgets(user_id, COALESCE(category_id, -1), period);

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS trigger_budgets_updated_at
AFTER UPDATE ON budgets
FOR EACH ROW
BEGIN
    UPDATE budgets SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Insert migration record
INSERT INTO schema_migrations (version, description, applied_at) 
VALUES ('002', 'create_budgets_table', CURRENT_TIMESTAMP);