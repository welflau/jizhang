# PRD — Setup database connection pool and base model

> 所属需求：后端 API 服务搭建

## 用户故事
As a backend developer, I want to set up a database connection pool with SQLAlchemy and create a base model class, so that all database operations can be performed efficiently and consistently across the application.

## 功能需求
- 使用 SQLAlchemy 配置异步数据库连接池（asyncpg 驱动）
- 创建 Base 模型类（app/models/base.py），包含通用字段（id, created_at, updated_at）
- 实现数据库会话管理（get_db 依赖注入函数）
- 编写数据库初始化脚本（create_tables 函数）
- 从环境变量读取数据库连接字符串（DATABASE_URL）
- 配置连接池参数（pool_size, max_overflow, pool_timeout）
- 实现数据库健康检查接口（/health/db）

## 验收标准
- [ ] 启动应用后 5s 内成功建立数据库连接池，连接数 ≥ 5
- [ ] Base 模型类包含字段：id (UUID primary key), created_at (datetime), updated_at (datetime)
- [ ] get_db() 依赖注入函数每次调用返回独立 session，请求结束后自动关闭
- [ ] 执行 create_tables() 后数据库中存在 alembic_version 表（迁移记录表）
- [ ] DATABASE_URL 未配置时应用启动失败，日志输出 ERROR 级别提示「DATABASE_URL not set」
- [ ] 连接池参数：pool_size=10, max_overflow=20, pool_timeout=30s
- [ ] GET /health/db 返回 200 + {"status": "healthy", "response_time_ms": <number>}，响应时间 < 100ms
- [ ] 数据库连接失败时 GET /health/db 返回 503 + {"status": "unhealthy", "error": "<error_message>"}
- [ ] 所有模型类继承 Base 后自动获得 id/created_at/updated_at 字段
- [ ] 数据库操作异常时抛出明确异常（DatabaseError），不吞异常

## 边界条件（不做的事）
- 不包含：具体业务表的模型定义（User/Project 等）
- 不包含：数据库迁移工具（Alembic）的完整配置（仅创建 alembic_version 表占位）
- 不包含：数据库备份/恢复功能
- 不包含：读写分离配置
- 暂不支持：多数据库切换
- 暂不支持：分库分表
- 超出范围：ORM 查询性能优化（N+1 问题等）

## 资产需求线索
暂无
