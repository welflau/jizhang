# PRD — Implement JWT authentication middleware

> 所属需求：后端 API 服务搭建

## 用户故事
As a backend developer, I want to implement JWT authentication middleware, So that the API can securely verify user identity and protect endpoints from unauthorized access.

## 功能需求
- JWT Token Generation: Create access token and refresh token with configurable expiration time
- JWT Token Verification: Validate token signature, expiration, and payload integrity
- Token Refresh: Allow users to obtain new access token using valid refresh token
- Password Hashing: Implement bcrypt-based password hashing and verification utilities
- Authentication Dependency: Provide `get_current_user` dependency function for FastAPI route protection
- Environment Configuration: Read JWT secret key, algorithm, and expiration settings from environment variables
- Error Handling: Return standardized error responses for invalid/expired tokens

## 验收标准
- [ ] `create_access_token(data: dict)` generates valid JWT token with expiration time from `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` env var (default 30 minutes)
- [ ] `create_refresh_token(data: dict)` generates refresh token with expiration time from `JWT_REFRESH_TOKEN_EXPIRE_DAYS` env var (default 7 days)
- [ ] `verify_token(token: str)` successfully decodes valid token and raises `HTTPException(401)` for invalid/expired tokens within 50ms
- [ ] `get_current_user` dependency extracts user info from Authorization header (format: "Bearer <token>") and returns user object, raises 401 if token missing/invalid
- [ ] `hash_password(password: str)` returns bcrypt hash with cost factor ≥ 12
- [ ] `verify_password(plain: str, hashed: str)` returns True for matching password within 200ms
- [ ] JWT secret key read from `JWT_SECRET_KEY` env var, raises startup error if missing
- [ ] JWT algorithm read from `JWT_ALGORITHM` env var (default "HS256")
- [ ] Token payload includes `sub` (subject/user_id), `exp` (expiration), and `iat` (issued at) claims
- [ ] Expired token returns JSON response `{"detail": "Token has expired"}` with status 401
- [ ] Invalid token signature returns JSON response `{"detail": "Invalid authentication credentials"}` with status 401
- [ ] Missing Authorization header returns JSON response `{"detail": "Not authenticated"}` with status 401

## 边界条件（不做的事）
- 不包含：用户注册/登录路由实现（由后续工单负责）
- 不包含：数据库用户模型查询逻辑（仅提供认证工具函数）
- 不包含：OAuth2/第三方登录集成
- 不包含：Token 黑名单/撤销机制（暂不支持主动登出）
- 不包含：权限/角色管理（RBAC）逻辑
- 不包含：Rate limiting / IP 白名单
- 暂不支持：Token 自动续期（需前端主动调用 refresh 接口）
- 超出范围：多设备登录管理、设备指纹识别

## 资产需求线索
暂无
