-- Migration: Create categories table
-- Description: Creates the categories table for storing income and expense categories
-- Version: 001
-- Created: 2024

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
    icon VARCHAR(50),
    color VARCHAR(20),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance optimization
CREATE INDEX idx_categories_user_id ON categories(user_id);
CREATE INDEX idx_categories_type ON categories(type);
CREATE INDEX idx_categories_user_type ON categories(user_id, type);
CREATE INDEX idx_categories_is_default ON categories(is_default);

-- Add comments for documentation
COMMENT ON TABLE categories IS 'Stores user-defined and default categories for income and expenses';
COMMENT ON COLUMN categories.id IS 'Primary key, auto-incrementing category ID';
COMMENT ON COLUMN categories.user_id IS 'Foreign key reference to users table';
COMMENT ON COLUMN categories.name IS 'Category name (e.g., Salary, Food, Transport)';
COMMENT ON COLUMN categories.type IS 'Category type: income or expense';
COMMENT ON COLUMN categories.icon IS 'Icon identifier for UI display';
COMMENT ON COLUMN categories.color IS 'Color code for category visualization';
COMMENT ON COLUMN categories.is_default IS 'Flag indicating if this is a system default category';
COMMENT ON COLUMN categories.created_at IS 'Timestamp when category was created';
COMMENT ON COLUMN categories.updated_at IS 'Timestamp when category was last updated';

-- Insert default expense categories
INSERT INTO categories (user_id, name, type, icon, color, is_default) VALUES
(0, 'Food & Dining', 'expense', 'restaurant', '#FF6B6B', TRUE),
(0, 'Transportation', 'expense', 'directions_car', '#4ECDC4', TRUE),
(0, 'Shopping', 'expense', 'shopping_cart', '#45B7D1', TRUE),
(0, 'Entertainment', 'expense', 'movie', '#FFA07A', TRUE),
(0, 'Healthcare', 'expense', 'local_hospital', '#98D8C8', TRUE),
(0, 'Education', 'expense', 'school', '#6C5CE7', TRUE),
(0, 'Bills & Utilities', 'expense', 'receipt', '#FDCB6E', TRUE),
(0, 'Housing', 'expense', 'home', '#A29BFE', TRUE),
(0, 'Insurance', 'expense', 'security', '#74B9FF', TRUE),
(0, 'Personal Care', 'expense', 'spa', '#FD79A8', TRUE),
(0, 'Travel', 'expense', 'flight', '#00B894', TRUE),
(0, 'Other Expenses', 'expense', 'more_horiz', '#B2BEC3', TRUE);

-- Insert default income categories
INSERT INTO categories (user_id, name, type, icon, color, is_default) VALUES
(0, 'Salary', 'income', 'account_balance_wallet', '#00D2D3', TRUE),
(0, 'Business', 'income', 'business_center', '#55EFC4', TRUE),
(0, 'Investment', 'income', 'trending_up', '#81ECEC', TRUE),
(0, 'Freelance', 'income', 'work', '#74B9FF', TRUE),
(0, 'Bonus', 'income', 'card_giftcard', '#A29BFE', TRUE),
(0, 'Rental Income', 'income', 'apartment', '#FFEAA7', TRUE),
(0, 'Refund', 'income', 'replay', '#DFE6E9', TRUE),
(0, 'Other Income', 'income', 'add_circle', '#B2BEC3', TRUE);

-- Create trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_categories_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER trigger_update_categories_timestamp
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE FUNCTION update_categories_updated_at();