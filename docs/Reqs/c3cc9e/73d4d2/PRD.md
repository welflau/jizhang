# PRD — Implement JWT authentication middleware

> 所属需求：后端 API 服务搭建

## 用户故事
As a backend developer, I want to implement JWT authentication middleware with secure token management and password hashing, So that the API can authenticate users securely and protect sensitive endpoints.

## 功能需求
- JWT token generation: create access token with configurable expiration time
- JWT token verification: validate token signature, expiration, and payload integrity
- JWT token refresh: issue new token before expiration without re-login
- Password hashing: use bcrypt to hash passwords with configurable salt rounds
- Password verification: compare plain password with hashed password
- Authentication dependency: provide `get_current_user()` function for route protection
- Environment variable configuration: read JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES from .env
- Error handling: return 401 for invalid/expired tokens, 403 for insufficient permissions

## 验收标准
- [ ] `create_access_token(data: dict)` generates valid JWT token with expiration time = ACCESS_TOKEN_EXPIRE_MINUTES (default 30 minutes)
- [ ] `verify_token(token: str)` returns decoded payload when token is valid, raises HTTPException(401) when token is expired/invalid
- [ ] `refresh_token(token: str)` issues new token with extended expiration time within 5 minutes before old token expires
- [ ] `hash_password(password: str)` returns bcrypt hashed string with salt rounds ≥ 12
- [ ] `verify_password(plain: str, hashed: str)` returns True for matching passwords, False otherwise, execution time ≥ 100ms (防止时序攻击)
- [ ] `get_current_user(token: str = Depends(oauth2_scheme))` dependency extracts user info from token, raises 401 if token invalid
- [ ] JWT_SECRET_KEY must be read from environment variable, raises ValueError if not set or length < 32 characters
- [ ] Token payload includes: sub (user_id), exp (expiration timestamp), iat (issued at timestamp)
- [ ] Invalid token returns JSON response: {"detail": "Could not validate credentials"} with status 401
- [ ] Expired token returns JSON response: {"detail": "Token has expired"} with status 401
- [ ] All functions have type hints and docstrings with @param and @return annotations
- [ ] Unit tests cover: valid token generation, expired token rejection, invalid signature rejection, password hash/verify correctness

## 边界条件（不做的事）
- 不包含：用户注册/登录路由实现（由其他工单负责）
- 不包含：权限角色管理（RBAC）逻辑
- 不包含：OAuth2 第三方登录集成
- 不包含：Token 黑名单/撤销机制（后续工单实现）
- 不包含：多设备登录管理
- 暂不支持：Refresh token 持久化存储（本期仅内存实现）
- 超出范围：Session 管理、Cookie 认证方案

## 资产需求线索
暂无
