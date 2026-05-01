# PRD — Setup database connection pool and base model

> 所属需求：后端 API 服务搭建

## 用户故事
As a backend developer, I want to set up a database connection pool with SQLAlchemy and create a base model class, so that all database operations can be performed efficiently and all models can inherit common functionality.

## 功能需求
- 使用 SQLAlchemy 配置异步数据库连接池（asyncpg 驱动）
- 创建 Base 模型类（app/models/base.py），包含通用字段（id, created_at, updated_at）
- 实现数据库会话管理（依赖注入 get_db()）
- 编写数据库初始化脚本（app/core/database.py）
- 数据库连接字符串从环境变量读取（DATABASE_URL）
- 提供数据库健康检查接口（/health/db）

## 验收标准
- [ ] 环境变量 DATABASE_URL 配置后，应用启动时成功建立数据库连接池（连接数 min=5, max=20）
- [ ] Base 模型类包含字段：id (UUID primary key), created_at (datetime), updated_at (datetime, 自动更新)
- [ ] get_db() 依赖注入函数每次请求返回独立 session，请求结束后自动关闭
- [ ] 数据库初始化脚本执行后，所有继承 Base 的模型表自动创建（支持 alembic 迁移）
- [ ] /health/db 接口调用时，执行 SELECT 1 查询，成功返回 {"status": "healthy", "latency_ms": <N>}，失败返回 503 状态码
- [ ] 数据库连接失败时，应用启动抛出明确异常信息（包含连接串的脱敏版本）
- [ ] 所有数据库操作使用 async/await，单次查询响应时间 < 100ms（本地环境）
- [ ] Base 模型的 __repr__() 方法返回可读字符串（包含 id 和类名）
- [ ] 连接池耗尽时（并发请求 > max_connections），新请求等待超时时间为 30s，超时返回 503
- [ ] 环境变量 DATABASE_URL 未配置时，应用启动失败并输出错误日志 "DATABASE_URL not set"

## 边界条件（不做的事）
- 不包含：具体业务模型的定义（User/Project 等模型由后续工单实现）
- 不包含：数据库迁移的自动执行逻辑（alembic upgrade 需手动或 CI 执行）
- 不包含：读写分离配置（当前仅支持单一数据库连接）
- 不包含：数据库备份/恢复功能
- 暂不支持：多数据库切换（multi-tenancy）
- 暂不支持：分库分表逻辑
- 超出范围：ORM 查询性能优化（索引设计由具体模型工单负责）

## 资产需求线索
暂无
