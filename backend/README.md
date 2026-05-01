# Backend Migration Guide

## Database Migrations

This project uses SQL-based migrations for database schema management.

### Running Migrations

```bash
# Run all pending migrations
python backend/migrations/run_migrations.py

# Or with custom database path
DB_PATH=/path/to/db.sqlite python backend/migrations/run_migrations.py
```

### Migration Files

Migrations are located in `backend/migrations/` and follow the naming convention:

```
001_initial_schema.sql
002_create_budgets_table.sql
003_add_feature_x.sql
```

**Naming Rules:**
- Start with a 3-digit number (001, 002, etc.)
- Use descriptive snake_case names
- Extension must be `.sql`

### Creating New Migrations

1. Create a new `.sql` file in `backend/migrations/`
2. Use the next sequential number (e.g., `003_add_tags.sql`)
3. Write idempotent SQL (use `IF NOT EXISTS` where applicable)
4. Add comments describing the migration purpose
5. Run the migration script to apply

### Migration Tracking

Applied migrations are tracked in the `schema_migrations` table:

```sql
CREATE TABLE schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Budgets Table Schema

The `002_create_budgets_table.sql` migration creates:

**Table: budgets**
- `id`: Primary key
- `user_id`: Foreign key to users table (NOT NULL)
- `category_id`: Foreign key to categories table (nullable for total budgets)
- `amount`: Budget amount (DECIMAL, >= 0)
- `period`: Budget period in YYYY-MM format (VARCHAR(7))
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp (auto-updated via trigger)

**Indexes:**
- `idx_budgets_user_id`: Single index on user_id
- `idx_budgets_period`: Single index on period
- `idx_budgets_user_period`: Composite index on (user_id, period) for optimal filtering
- `idx_budgets_category_id`: Single index on category_id

**Constraints:**
- `amount >= 0`: Non-negative budget amounts
- `period` format: Must match YYYY-MM pattern
- Foreign key cascades: DELETE CASCADE on user_id, SET NULL on category_id

### Best Practices

1. **Never modify applied migrations** - Create a new migration instead
2. **Test migrations locally** before deploying
3. **Backup database** before running migrations in production
4. **Use transactions** - The migration runner wraps each file in a transaction
5. **Add indexes** for frequently queried columns
6. **Document breaking changes** in migration comments

### Rollback

Currently, rollback is manual:

1. Identify the migration to rollback
2. Write reverse SQL statements
3. Execute manually or create a down migration
4. Remove entry from `schema_migrations` table

Future enhancement: Add `down.sql` support for automatic rollbacks.
