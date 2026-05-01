# PRD — Setup database connection pool and base model

> 所属需求：后端 API 服务搭建

## 用户故事
As a backend developer, I want to set up a database connection pool with SQLAlchemy and create a base model class, So that all database operations can be performed efficiently with proper session management and all models can inherit common functionality.

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
- [ ] Base 模型类包含字段：id (UUID primary key), created_at (datetime), updated_at (datetime, auto-update)
- [ ] get_db() 依赖注入函数每次请求返回独立 session，请求结束后自动关闭
- [ ] 执行 create_tables() 后数据库中存在 alembic_version 表（迁移管理）
- [ ] DATABASE_URL 未配置时启动失败并输出错误日志「DATABASE_URL not found in environment variables」
- [ ] 连接池配置：pool_size=10, max_overflow=20, pool_timeout=30s
- [ ] GET /health/db 返回 200 + {"status": "healthy", "response_time_ms": <number>}，响应时间 < 100ms
- [ ] 数据库连接失败时 GET /health/db 返回 503 + {"status": "unhealthy", "error": "<error_message>"}
- [ ] 所有数据库操作异常时自动回滚事务并记录 error 级别日志
- [ ] Base 模型的 __repr__() 方法输出格式：<ModelName(id=xxx)>
- [ ] 继承 Base 的模型类自动拥有 created_at 和 updated_at 字段，更新记录时 updated_at 自动刷新
- [ ] 连接池耗尽时新请求等待最多 30s，超时返回 503 错误

## 边界条件（不做的事）
- 不包含：具体业务模型定义（User/Project 等模型由后续工单实现）
- 不包含：数据库迁移工具配置（Alembic 配置由独立工单处理）
- 不包含：读写分离配置（当前仅支持单数据库连接）
- 不包含：数据库备份/恢复脚本
- 暂不支持：多数据库切换、分库分表
- 超出范围：ORM 性能优化（N+1 查询优化等）、慢查询日志分析

## 资产需求线索
暂无
