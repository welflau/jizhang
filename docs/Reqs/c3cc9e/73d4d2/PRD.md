# PRD — Implement JWT authentication middleware

> 所属需求：后端 API 服务搭建

## 用户故事
As a backend developer, I want to implement JWT authentication middleware with token generation, verification, and refresh logic, So that the API can securely authenticate users and protect endpoints with role-based access control.

## 功能需求
- JWT token generation: create access token and refresh token with configurable expiration time
- JWT token verification: validate token signature, expiration, and extract user claims
- JWT token refresh: exchange valid refresh token for new access token
- Password hashing: use bcrypt to hash and verify passwords with configurable salt rounds
- Authentication dependency: provide `get_current_user` function for FastAPI route protection
- Environment configuration: read JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS from environment variables
- Token payload: include user_id, username, role, exp, iat fields
- Error handling: return specific HTTP 401 errors for expired/invalid/missing tokens

## 验收标准
- [ ] `create_access_token(data: dict)` generates valid JWT token with expiration time = ACCESS_TOKEN_EXPIRE_MINUTES (default 30 minutes)
- [ ] `create_refresh_token(data: dict)` generates valid JWT token with expiration time = REFRESH_TOKEN_EXPIRE_DAYS (default 7 days)
- [ ] `verify_token(token: str)` returns decoded payload when token is valid, raises HTTPException(401) when expired/invalid
- [ ] `get_current_user` dependency extracts token from Authorization header (format: "Bearer <token>"), returns user object, raises HTTPException(401) if token missing/invalid
- [ ] `hash_password(password: str)` returns bcrypt hashed string with cost factor ≥ 12
- [ ] `verify_password(plain_password: str, hashed_password: str)` returns True for matching passwords, False otherwise, execution time ≥ 100ms (防timing attack)
- [ ] JWT_SECRET_KEY read from environment variable, raises ValueError if not set or length < 32 characters
- [ ] Token payload includes required fields: user_id (int), username (str), role (str), exp (int), iat (int)
- [ ] Expired token verification raises HTTPException with status_code=401, detail="Token has expired"
- [ ] Invalid signature verification raises HTTPException with status_code=401, detail="Invalid token signature"
- [ ] Missing Authorization header raises HTTPException with status_code=401, detail="Authorization header missing"
- [ ] Malformed Authorization header (not "Bearer <token>") raises HTTPException with status_code=401, detail="Invalid authorization header format"

## 边界条件（不做的事）
- 不包含：用户注册/登录路由实现（由其他工单负责）
- 不包含：数据库用户模型定义（由 models 工单负责）
- 不包含：权限装饰器实现（如 @require_role("admin")，后续工单扩展）
- 不包含：Token 黑名单机制（logout 后 token 仍有效直到过期）
- 不包含：OAuth2/第三方登录集成
- 暂不支持：Token 自动续期（sliding session）
- 暂不支持：多设备登录管理
- 超出范围：RBAC 权限表设计、API 限流、审计日志

## 资产需求线索
暂无
