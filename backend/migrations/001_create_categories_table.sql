-- Migration: Create categories table
-- Created at: 2024-01-01
-- Description: Create categories table with user_id, name, type, icon, color, and is_default fields

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK(type IN ('income', 'expense')),
    icon VARCHAR(50),
    color VARCHAR(20),
    is_default BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id);
CREATE INDEX IF NOT EXISTS idx_categories_type ON categories(type);
CREATE INDEX IF NOT EXISTS idx_categories_user_type ON categories(user_id, type);
CREATE INDEX IF NOT EXISTS idx_categories_is_default ON categories(is_default);

-- Create trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_categories_timestamp 
AFTER UPDATE ON categories
FOR EACH ROW
BEGIN
    UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Insert default expense categories
INSERT INTO categories (user_id, name, type, icon, color, is_default) VALUES
(0, '餐饮', 'expense', '🍔', '#FF6B6B', 1),
(0, '交通', 'expense', '🚗', '#4ECDC4', 1),
(0, '购物', 'expense', '🛍️', '#45B7D1', 1),
(0, '娱乐', 'expense', '🎮', '#96CEB4', 1),
(0, '医疗', 'expense', '💊', '#FFEAA7', 1),
(0, '教育', 'expense', '📚', '#DFE6E9', 1),
(0, '住房', 'expense', '🏠', '#74B9FF', 1),
(0, '通讯', 'expense', '📱', '#A29BFE', 1),
(0, '其他', 'expense', '📝', '#B2BEC3', 1);

-- Insert default income categories
INSERT INTO categories (user_id, name, type, icon, color, is_default) VALUES
(0, '工资', 'income', '💰', '#00B894', 1),
(0, '奖金', 'income', '🎁', '#00CEC9', 1),
(0, '投资', 'income', '📈', '#0984E3', 1),
(0, '兼职', 'income', '💼', '#6C5CE7', 1),
(0, '其他', 'income', '📝', '#B2BEC3', 1);