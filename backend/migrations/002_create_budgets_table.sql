-- Migration: Create budgets table
-- Created: 2024-01-01
-- Description: Add budgets table with user_id, category_id, amount, period, and timestamps

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER,
    amount REAL NOT NULL CHECK(amount >= 0),
    period TEXT NOT NULL CHECK(period GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
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

-- Create trigger to auto-update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_budgets_timestamp
AFTER UPDATE ON budgets
FOR EACH ROW
BEGIN
    UPDATE budgets SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Insert sample data for testing (optional, can be removed in production)
INSERT INTO budgets (user_id, category_id, amount, period) VALUES
(1, 1, 5000.00, '2024-01'),
(1, 2, 2000.00, '2024-01'),
(1, NULL, 10000.00, '2024-02');
