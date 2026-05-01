-- Add indexes for bill query optimization
-- Run this migration to improve query performance

-- Index on date field for time range queries
CREATE INDEX IF NOT EXISTS idx_bills_date ON bills(date DESC);

-- Index on category for category filtering
CREATE INDEX IF NOT EXISTS idx_bills_category ON bills(category);

-- Index on bill_type for type filtering
CREATE INDEX IF NOT EXISTS idx_bills_type ON bills(bill_type);

-- Index on amount for amount range queries
CREATE INDEX IF NOT EXISTS idx_bills_amount ON bills(amount);

-- Composite index for common query patterns (type + date)
CREATE INDEX IF NOT EXISTS idx_bills_type_date ON bills(bill_type, date DESC);

-- Composite index for category + date queries
CREATE INDEX IF NOT EXISTS idx_bills_category_date ON bills(category, date DESC);

-- Index on created_at for sorting by creation time
CREATE INDEX IF NOT EXISTS idx_bills_created_at ON bills(created_at DESC);

-- Full-text search index on description (if SQLite FTS is available)
-- For keyword search optimization
-- Note: This requires SQLite FTS extension, comment out if not available
-- CREATE VIRTUAL TABLE IF NOT EXISTS bills_fts USING fts5(description, content=bills, content_rowid=id);
