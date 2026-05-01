# Personal Finance Manager

A full-stack personal finance management application with budget tracking, transaction management, and spending analytics.

## Features

- **Budget Management**: Set monthly budgets by category or overall spending limits
- **Transaction Tracking**: Record income and expenses with categorization
- **Spending Analytics**: View budget usage, remaining amounts, and spending percentages
- **Period-based Tracking**: Organize budgets and transactions by month (YYYY-MM format)

## Tech Stack

**Backend**:
- Python 3.11+
- FastAPI (async web framework)
- SQLite with aiosqlite (async database)
- Pydantic v2 (data validation)

**Frontend**:
- Single-page HTML with inline JavaScript
- Vanilla JS (no build tools required)
- Responsive CSS

## Project Structure

```
.
├── backend/
│   ├── migrations/          # Database migration SQL files
│   │   ├── 001_initial_schema.sql
│   │   └── 002_create_budgets_table.sql
│   ├── models/              # Pydantic schemas
│   │   └── budget.py
│   ├── routes/              # API route handlers
│   │   └── budgets.py
│   ├── db_migration.py      # Migration runner script
│   ├── dependencies.py      # FastAPI dependencies
│   └── main.py              # Application entry point
├── frontend/
│   └── index.html           # Single-page frontend
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
pip install fastapi uvicorn aiosqlite pydantic
```

### 2. Run Database Migrations

```bash
python backend/db_migration.py
```

This will:
- Create the SQLite database at `backend/app.db`
- Execute all migration files in `backend/migrations/`
- Set up tables: users, categories, transactions, budgets
- Create necessary indexes for query optimization

### 3. Start the Backend Server

```bash
python backend/main.py
```

Or with uvicorn directly:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8080
```

API will be available at: `http://localhost:8080`

### 4. Open Frontend

Open `frontend/index.html` in your browser, or serve it with:

```bash
python -m http.server 3000 --directory frontend
```

Then visit: `http://localhost:3000`

## API Endpoints

### Budgets

- `POST /api/budgets` - Create a new budget
- `GET /api/budgets` - List all budgets (with optional filters: `period`, `category_id`)
- `GET /api/budgets/{budget_id}` - Get specific budget with spending info
- `PUT /api/budgets/{budget_id}` - Update budget
- `DELETE /api/budgets/{budget_id}` - Delete budget

### Authentication

All endpoints require an `Authorization` header:

```
Authorization: Bearer <user_id>
```

*Note: This is a simplified auth for development. Production should use JWT or OAuth2.*

## Database Schema

### budgets Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| category_id | INTEGER | Foreign key to categories (nullable) |
| amount | REAL | Budget amount (non-negative) |
| period | TEXT | Budget period (YYYY-MM format) |
| created_at | TEXT | Creation timestamp |
| updated_at | TEXT | Last update timestamp |

**Indexes**:
- `idx_budgets_user_id` on `user_id`
- `idx_budgets_period` on `period`
- `idx_budgets_user_period` on `(user_id, period)` - composite index for optimal queries
- `idx_budgets_category_id` on `category_id`

**Constraints**:
- `amount >= 0` (check constraint)
- `period` must match `YYYY-MM` format (check constraint)
- Foreign key cascade: deleting user deletes their budgets
- Foreign key set null: deleting category sets budget's category_id to NULL

## Development

### Adding New Migrations

1. Create a new SQL file in `backend/migrations/` with sequential numbering:
   ```
   003_add_new_feature.sql
   ```

2. Run migrations:
   ```bash
   python backend/db_migration.py
   ```

### Rolling Back Migrations

```bash
python backend/db_migration.py rollback
```

*Note: This only removes the tracking record. Manual schema rollback required.*

### Running Tests

```bash
pytest backend/tests/
```

## Environment Variables

- `DB_PATH` - Database file path (default: `backend/app.db`)
- `PORT` - Server port (default: `8080`)

## License

MIT
