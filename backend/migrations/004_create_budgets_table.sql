-- Migration: Create budgets table
-- Description: Create budgets table with user_id, category_id, amount, period, and timestamps
-- Created: 2024

-- Create budgets table
CREATE TABLE IF NOT EXISTS budgets (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    category_id BIGINT,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount >= 0),
    period VARCHAR(7) NOT NULL CHECK (period ~ '^\d{4}-(0[1-9]|1[0-2])$'),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_budgets_user_id 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_budgets_category_id 
        FOREIGN KEY (category_id) 
        REFERENCES categories(id) 
        ON DELETE CASCADE,
    
    -- Unique constraint: one budget per user per category per period
    -- If category_id is NULL, it represents a total budget for the period
    CONSTRAINT unique_user_category_period 
        UNIQUE NULLS NOT DISTINCT (user_id, category_id, period)
);

-- Create indexes for optimized query performance
CREATE INDEX idx_budgets_user_id ON budgets(user_id);
CREATE INDEX idx_budgets_period ON budgets(period);
CREATE INDEX idx_budgets_user_period ON budgets(user_id, period);
CREATE INDEX idx_budgets_category_id ON budgets(category_id) WHERE category_id IS NOT NULL;

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_budgets_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_budgets_updated_at
    BEFORE UPDATE ON budgets
    FOR EACH ROW
    EXECUTE FUNCTION update_budgets_updated_at();

-- Add comments for documentation
COMMENT ON TABLE budgets IS 'Stores user budget information for different categories and periods';
COMMENT ON COLUMN budgets.id IS 'Primary key';
COMMENT ON COLUMN budgets.user_id IS 'Foreign key reference to users table';
COMMENT ON COLUMN budgets.category_id IS 'Optional foreign key reference to categories table. NULL means total budget for the period';
COMMENT ON COLUMN budgets.amount IS 'Budget amount in decimal format';
COMMENT ON COLUMN budgets.period IS 'Budget period in YYYY-MM format';
COMMENT ON COLUMN budgets.created_at IS 'Timestamp when the budget was created';
COMMENT ON COLUMN budgets.updated_at IS 'Timestamp when the budget was last updated';