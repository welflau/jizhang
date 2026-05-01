-- Migration: Create transactions table
-- Description: Create transactions table with all required fields and indexes for optimal query performance

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    category_id BIGINT NOT NULL,
    date DATE NOT NULL,
    note TEXT,
    payment_method VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_transactions_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    
    CONSTRAINT fk_transactions_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE RESTRICT
);

-- Create indexes for optimal query performance
-- Index on user_id for filtering transactions by user
CREATE INDEX idx_transactions_user_id ON transactions(user_id);

-- Index on date for date range queries and sorting
CREATE INDEX idx_transactions_date ON transactions(date DESC);

-- Composite index on user_id and date for common query patterns
CREATE INDEX idx_transactions_user_date ON transactions(user_id, date DESC);

-- Index on type for filtering by income/expense
CREATE INDEX idx_transactions_type ON transactions(type);

-- Composite index on user_id, type, and date for filtered queries
CREATE INDEX idx_transactions_user_type_date ON transactions(user_id, type, date DESC);

-- Index on category_id for category-based queries
CREATE INDEX idx_transactions_category_id ON transactions(category_id);

-- Composite index on user_id and category_id for user's category analysis
CREATE INDEX idx_transactions_user_category ON transactions(user_id, category_id);

-- Index on created_at for audit and recent transaction queries
CREATE INDEX idx_transactions_created_at ON transactions(created_at DESC);

-- Create trigger function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_transactions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to call the function before update
CREATE TRIGGER trigger_update_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_transactions_updated_at();

-- Add comments for documentation
COMMENT ON TABLE transactions IS 'Stores all income and expense transaction records';
COMMENT ON COLUMN transactions.id IS 'Primary key, auto-incrementing transaction ID';
COMMENT ON COLUMN transactions.user_id IS 'Foreign key reference to users table';
COMMENT ON COLUMN transactions.type IS 'Transaction type: income or expense';
COMMENT ON COLUMN transactions.amount IS 'Transaction amount, must be positive';
COMMENT ON COLUMN transactions.category_id IS 'Foreign key reference to categories table';
COMMENT ON COLUMN transactions.date IS 'Date when the transaction occurred';
COMMENT ON COLUMN transactions.note IS 'Optional note or description for the transaction';
COMMENT ON COLUMN transactions.payment_method IS 'Payment method used (e.g., cash, credit card, bank transfer)';
COMMENT ON COLUMN transactions.created_at IS 'Timestamp when the record was created';
COMMENT ON COLUMN transactions.updated_at IS 'Timestamp when the record was last updated';