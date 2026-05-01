# Backend - Personal Finance Manager

## Database Migrations

### Running Migrations

To apply all pending migrations:

```bash
python backend/db/migrate.py
```

To reset database and re-run all migrations:

```bash
python backend/db/migrate.py --reset
```

### Migration Files

Migrations are stored in `backend/migrations/` directory:

- `001_init_schema.sql` - Initial database schema (users, categories, transactions)
- `002_create_budgets_table.sql` - Budgets table with indexes

### Database Schema

#### budgets Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users table |
| category_id | INTEGER | Optional foreign key to categories table |
| amount | DECIMAL(10,2) | Budget amount (must be >= 0) |
| period | VARCHAR(7) | Budget period in YYYY-MM format |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

#### Indexes

- `idx_budgets_user_id` - Fast user-specific queries
- `idx_budgets_period` - Fast period-based queries
- `idx_budgets_user_period` - Composite index for optimal user+period queries
- `idx_budgets_category_id` - Category-based filtering
- `idx_budgets_unique_user_category_period` - Prevent duplicate budgets

#### Constraints

- `amount >= 0` - Budget amount must be non-negative
- `period` format validation - Must match YYYY-MM pattern
- Unique constraint on (user_id, category_id, period) - One budget per user/category/period
- Foreign key cascades:
  - `user_id` ON DELETE CASCADE - Delete budgets when user is deleted
  - `category_id` ON DELETE SET NULL - Set to NULL when category is deleted

### Environment Variables

- `DB_PATH` - Database file path (default: `backend/data/app.db`)

### Development

1. Create new migration file in `backend/migrations/`:
   - Naming: `XXX_description.sql` (e.g., `003_add_tags_table.sql`)
   - Include migration record insert at the end

2. Run migration:
   ```bash
   python backend/db/migrate.py
   ```

3. Verify:
   ```bash
   sqlite3 backend/data/app.db "SELECT * FROM schema_migrations;"
   ```
