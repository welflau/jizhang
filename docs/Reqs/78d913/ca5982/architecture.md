# 架构设计 - Implement transaction CRUD API endpoints

## 架构模式
RESTful API with layered architecture (Router -> Service -> Model)

## 技术栈

- **backend**: FastAPI
- **database**: aiosqlite (SQLite async)
- **validation**: Pydantic
- **authentication**: JWT (existing pattern)
- **orm**: Raw SQL (consistent with existing budget/category implementation)

## 模块设计

### 
职责: Transaction data model and database operations (CRUD)

### 
职责: Request/response schemas for transaction API

### 
职责: Transaction API endpoints with auth and validation

### 
职责: Database schema for transactions table

### 
职责: Register transactions router

## 关键决策
- {'decision': 'Use raw SQL instead of ORM', 'rationale': 'Consistent with existing budget/category implementation in codebase, avoids introducing new dependency'}
- {'decision': 'Implement soft delete vs hard delete', 'rationale': 'Use hard delete (actual DELETE SQL) for simplicity, add deleted_at column only if audit trail needed later'}
- {'decision': 'Pagination strategy: offset-based', 'rationale': 'Simple to implement, sufficient for typical use case. Cursor-based can be added if performance issues arise'}
- {'decision': 'Authorization pattern: JWT user_id extraction', 'rationale': 'Reuse existing JWT auth pattern from backend/main.py (get_current_user dependency)'}
- {'decision': 'Transaction type enum: store as string', 'rationale': "Store 'income'/'expense' as VARCHAR for readability, add CHECK constraint for validation"}
- {'decision': 'Amount field: DECIMAL vs INTEGER', 'rationale': 'Use REAL (SQLite) to store decimal amounts, handle precision in application layer (round to 2 decimals)'}
