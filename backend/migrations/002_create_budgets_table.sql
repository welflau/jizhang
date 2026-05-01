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

-- Create composite index on user_id and period for optimal filtering
CREATE INDEX IF NOT EXISTS idx_budgets_user_period ON budgets(user_id, period);

-- Create index on category_id for category-based budget queries
CREATE INDEX IF NOT EXISTS idx_budgets_category_id ON budgets(category_id);

-- Create trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_budgets_timestamp
AFTER UPDATE ON budgets
FOR EACH ROW
BEGIN
    UPDATE budgets SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Insert sample data for testing (optional, can be removed in production)
INSERT INTO budgets (user_id, category_id, amount, period) VALUES
(1, 1, 5000.00, '2024-01'),
(1, 2, 3000.00, '2024-01'),
(1, 3, 2000.00, '2024-01'),
(1, NULL, 15000.00, '2024-01');
