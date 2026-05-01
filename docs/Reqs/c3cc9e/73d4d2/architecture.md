# 架构设计 - Implement JWT authentication middleware

## 架构模式
middleware_and_security_layer

## 技术栈

- **core**: FastAPI, Python 3.9+
- **security**: python-jose[cryptography], passlib[bcrypt], python-multipart
- **validation**: pydantic, email-validator
- **async**: asyncio

## 模块设计

### 
职责: JWT token generation, verification, refresh logic and password hashing utilities

### 
职责: FastAPI dependency functions for authentication

### 
职责: Add JWT-related configuration fields

### 
职责: Pydantic schemas for token request/response

### 
职责: Custom authentication exceptions

## 关键决策
- {'decision': 'Use python-jose for JWT instead of PyJWT', 'rationale': 'python-jose provides better integration with FastAPI ecosystem and includes cryptography support out of box'}
- {'decision': 'Separate access token (short-lived) and refresh token (long-lived)', 'rationale': 'Security best practice: minimize exposure window for access tokens while allowing persistent sessions via refresh tokens'}
- {'decision': 'Use passlib with bcrypt backend for password hashing', 'rationale': 'Industry standard, adaptive hashing with configurable rounds, better than plain bcrypt library for future algorithm migration'}
- {'decision': "Store user identifier (user_id or email) in token 'sub' claim", 'rationale': 'JWT standard claim for subject identification, allows stateless authentication without database lookup on every request'}
- {'decision': 'Create separate dependencies.py instead of putting dependencies in security.py', 'rationale': 'Separation of concerns: security.py handles crypto operations, dependencies.py handles FastAPI integration'}
- {'decision': "Token type field in payload ('access' vs 'refresh')", 'rationale': 'Prevents refresh token from being used as access token and vice versa, adds security layer'}
