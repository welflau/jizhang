# 架构设计 - Implement category CRUD API endpoints

## 架构模式
RESTful API with layered architecture (Router -> Service -> Repository)

## 技术栈

- **framework**: FastAPI
- **orm**: SQLAlchemy (async)
- **validation**: Pydantic v2
- **database**: PostgreSQL (via existing alembic migrations)
- **authentication**: JWT (existing auth router pattern)

## 模块设计

### 
职责: SQLAlchemy ORM model for categories table

### 
职责: Pydantic schemas for request/response validation

### 
职责: Database access layer for category operations

### 
职责: Business logic layer for category management

### 
职责: API endpoints for category CRUD

### 
职责: Add async session dependency for repositories

## 关键决策
- {'decision': 'Use soft delete vs hard delete for categories', 'chosen': 'Hard delete with pre-check (block if has transactions)', 'rationale': 'Simpler data model, clear user intent. Transactions table already has category_id FK with ON DELETE RESTRICT constraint from migration 003.', 'alternatives': 'Soft delete (is_deleted flag) - adds complexity, requires filtering in all queries'}
- {'decision': 'Default categories creation timing', 'chosen': 'Seed on user registration (call seed_default_categories in auth signup flow)', 'rationale': 'Ensures every user has working categories immediately, no empty state handling needed', 'alternatives': 'Lazy creation on first access - worse UX, requires null checks'}
- {'decision': 'Category uniqueness scope', 'chosen': 'Unique per (user_id, name, type) - same name allowed for income vs expense', 'rationale': "Users may want '奖金' as income and '奖金支出' as expense, type separation provides flexibility", 'alternatives': 'Unique per (user_id, name) - too restrictive'}
- {'decision': 'Icon/color storage format', 'chosen': 'Store as string (icon: emoji or icon-name, color: hex code #RRGGBB)', 'rationale': 'Simple, frontend-agnostic. Icon set design is in parallel task, use string for flexibility', 'alternatives': 'Integer enum - requires backend/frontend sync, less flexible'}
- {'decision': 'API response structure for list endpoint', 'chosen': 'Grouped by type: {income: [...], expense: [...]}', 'rationale': 'Frontend typically displays categories in separate sections, pre-grouping reduces client-side processing', 'alternatives': 'Flat list with type field - requires frontend grouping logic'}
