# 架构设计 - Create categories database table and migration

## 架构模式
Incremental Database Layer Extension

## 技术栈

- **database**: SQLite (aiosqlite)
- **migration**: Raw SQL with version tracking
- **orm**: None (direct SQL queries)
- **indexing**: B-tree indexes on user_id and type

## 模块设计

### database/migrations
职责: 
- async def run_migrations(db_path: str) -> None
- async def get_current_version(db: aiosqlite.Connection) -> int

### database/schema
职责: 
- CATEGORIES_TABLE_DDL: str
- CATEGORIES_INDEXES: List[str]

### startup_integration
职责: 

## 关键决策
- {'decision': 'Use raw SQL migrations instead of ORM migration tools', 'rationale': 'Project already uses aiosqlite directly without ORM layer; introducing Alembic/SQLAlchemy would add unnecessary complexity and dependencies', 'alternatives': ['Alembic with SQLAlchemy', 'Yoyo migrations'], 'trade_offs': 'Manual SQL writing required but maintains consistency with existing codebase architecture'}
- {'decision': 'Store migration version in dedicated schema_migrations table', 'rationale': 'Standard pattern for tracking applied migrations; allows rollback capability and prevents duplicate execution', 'alternatives': ['File-based version tracking', 'Application config table'], 'trade_offs': 'Adds one extra table but provides reliable migration state management'}
- {'decision': 'Use TEXT type for type column with CHECK constraint', 'rationale': "SQLite doesn't have native ENUM; CHECK constraint enforces data integrity at database level", 'alternatives': ['Integer with mapping table', 'No constraint (application-level validation only)'], 'trade_offs': 'Slightly less performant than integer but more readable and maintainable'}
- {'decision': 'Create composite index on (user_id, type)', 'rationale': "Primary query pattern will be 'get all income/expense categories for user X'; composite index optimizes this exact use case", 'alternatives': ['Separate indexes on user_id and type', 'Single index on user_id only'], 'trade_offs': 'Increases write overhead slightly but dramatically improves read performance for filtered queries'}
- {'decision': 'Use INTEGER for is_default instead of BOOLEAN', 'rationale': "SQLite stores booleans as integers (0/1); explicit INTEGER type matches SQLite's internal representation", 'alternatives': ["TEXT 'true'/'false'", 'BOOLEAN type alias'], 'trade_offs': 'Requires application-level boolean conversion but aligns with SQLite best practices'}
- {'decision': 'Add created_at timestamp with DEFAULT CURRENT_TIMESTAMP', 'rationale': 'Audit trail for category creation; useful for debugging and future analytics features', 'alternatives': ['No timestamp', 'Application-managed timestamp'], 'trade_offs': 'Minimal storage overhead; database-managed timestamps are more reliable than application-managed'}
