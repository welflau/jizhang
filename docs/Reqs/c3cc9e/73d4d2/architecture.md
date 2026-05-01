# 架构设计 - Implement JWT authentication middleware

## 架构模式
Layered Architecture with Middleware Pattern

## 技术栈

- **framework**: FastAPI
- **authentication**: JWT (PyJWT)
- **password_hashing**: bcrypt
- **validation**: Pydantic
- **async_support**: asyncio

## 模块设计

### 
职责: JWT token generation, verification, refresh logic and password hashing utilities

### 
职责: FastAPI dependency injection functions for authentication

### 
职责: Pydantic schemas for token request/response

### 
职责: Add JWT configuration from environment variables

## 关键决策
- {'decision': 'Use bcrypt for password hashing instead of passlib', 'rationale': 'bcrypt is simpler, well-audited, and sufficient for password hashing without additional dependencies. Already used in backend/main.py'}
- {'decision': 'Separate access token (short-lived) and refresh token (long-lived)', 'rationale': 'Security best practice: limits exposure window if access token is compromised, refresh token stored securely for token renewal'}
- {'decision': 'Store JWT configuration in environment variables via app/core/config.py', 'rationale': 'Follows global security rule: never hardcode secrets, centralized configuration management'}
- {'decision': 'Create dedicated dependencies.py for auth dependency functions', 'rationale': 'Separation of concerns: security.py handles crypto operations, dependencies.py handles FastAPI integration and user retrieval'}
- {'decision': 'Token payload includes user_id (sub), expiration (exp), and token type', 'rationale': 'Minimal payload reduces token size, type field distinguishes access vs refresh tokens, follows JWT standard claims'}
- {'decision': 'Use HTTPBearer security scheme for automatic Swagger UI integration', 'rationale': "FastAPI native support, auto-generates 'Authorize' button in docs, cleaner than manual header parsing"}
