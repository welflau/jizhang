# FastAPI Backend with SQLAlchemy Async

## Features

- ✅ FastAPI async framework
- ✅ SQLAlchemy 2.0 with async support
- ✅ Database connection pool configuration
- ✅ Declarative Base model for ORM
- ✅ Dependency injection for database sessions
- ✅ Database initialization script
- ✅ Environment-based configuration
- ✅ Lifespan event handlers for startup/shutdown

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   └── config.py          # Configuration management
│   ├── models/
│   │   ├── __init__.py        # Models package exports
│   │   ├── base.py            # Declarative Base class
│   │   └── user.py            # Example User model
│   ├── database.py            # Database connection pool & session
│   └── main.py                # FastAPI application entry
├── scripts/
│   └── init_db.py             # Database initialization script
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env to set your DATABASE_URL
```

### 3. Initialize Database

```bash
# Run initialization script to create tables
python scripts/init_db.py
```

### 4. Start Server

```bash
# Development mode (auto-reload)
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## Database Configuration

### SQLite (Default)

```env
DATABASE_URL=sqlite+aiosqlite:///./app.db
```

### PostgreSQL

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
```

### MySQL

```env
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/dbname
```

## Usage Examples

### Creating a New Model

```python
# app/models/product.py
from sqlalchemy import Column, Integer, String, Float
from app.models.base import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
```

### Using Database Session in Routes

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User

@app.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

@app.post("/users")
async def create_user(username: str, email: str, db: AsyncSession = Depends(get_db)):
    user = User(username=username, email=email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## Testing Database Connection

```bash
# Check if server starts successfully
curl http://localhost:8080/

# Expected response:
# {"status":"ok","app":"FastAPI Application","database":"connected"}
```

## Key Implementation Details

### Connection Pool Configuration

- **SQLite**: Uses `NullPool` (no pooling for file-based DB)
- **PostgreSQL/MySQL**: 
  - `pool_size=10` (10 persistent connections)
  - `max_overflow=20` (up to 30 total connections)
  - `pool_pre_ping=True` (verify connection before use)

### Session Management

- Auto-commit on success
- Auto-rollback on exception
- Proper cleanup in finally block

### Lifespan Events

- **Startup**: Initialize DB connection pool and create tables
- **Shutdown**: Close all connections gracefully

## Troubleshooting

### Database Locked (SQLite)

Increase busy timeout in database.py:

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"timeout": 30}  # 30 seconds
)
```

### Connection Pool Exhausted

Increase pool size in database.py:

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=40
)
```
