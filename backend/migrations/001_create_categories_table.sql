-- Migration: Create categories table
-- Description: Creates the categories table for storing income and expense categories

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
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

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE categories IS 'Stores user-defined and default income/expense categories';
COMMENT ON COLUMN categories.id IS 'Primary key';
COMMENT ON COLUMN categories.user_id IS 'Reference to user who owns this category';
COMMENT ON COLUMN categories.name IS 'Category name';
COMMENT ON COLUMN categories.type IS 'Category type: income or expense';
COMMENT ON COLUMN categories.icon IS 'Icon identifier for UI display';
COMMENT ON COLUMN categories.color IS 'Color code for UI display';
COMMENT ON COLUMN categories.is_default IS 'Whether this is a system default category';
COMMENT ON COLUMN categories.created_at IS 'Timestamp when category was created';
COMMENT ON COLUMN categories.updated_at IS 'Timestamp when category was last updated';