# PRD — Setup database connection pool and base model

> 所属需求：后端 API 服务搭建

## 用户故事
As a backend developer, I want to set up a database connection pool with proper session management, So that the FastAPI application can reliably interact with the database with optimal performance and resource utilization.

## 功能需求
- 使用 SQLAlchemy 异步引擎配置数据库连接池
- 创建 Base 模型类（app/models/base.py），包含通用字段（id, created_at, updated_at）
- 实现数据库会话管理（get_db 依赖注入函数）
- 编写数据库初始化脚本（init_db.py），支持建表和迁移
- 从环境变量读取数据库连接字符串（DATABASE_URL）
- 配置连接池参数：pool_size, max_overflow, pool_timeout, pool_recycle
- 实现数据库健康检查接口（/health/db）
- 添加数据库连接错误处理和重试机制

## 验收标准
- [ ] 应用启动时成功建立数据库连接池，连接数 ≥ 5 且 ≤ pool_size 配置值
- [ ] Base 模型类包含字段：id (UUID/Integer primary key), created_at (datetime), updated_at (datetime, 自动更新)
- [ ] get_db() 依赖注入函数在请求结束后自动关闭会话，无连接泄漏（通过 finally 块保证）
- [ ] init_db.py 脚本执行后所有继承 Base 的模型对应的表在数据库中创建成功
- [ ] DATABASE_URL 环境变量缺失时应用启动失败并输出明确错误日志（包含 "DATABASE_URL not found"）
- [ ] 连接池耗尽时（并发请求数 > pool_size + max_overflow），新请求等待时间 ≤ pool_timeout 秒后返回 503 错误
- [ ] 数据库连接空闲时间 ≥ pool_recycle 秒后自动回收重建（防止 MySQL "gone away" 错误）
- [ ] GET /health/db 接口返回 200 且响应时间 < 500ms 时表示数据库连接正常
- [ ] 数据库连接失败时自动重试 3 次，每次间隔 2 秒，3 次失败后记录 error 级别日志
- [ ] app/models/base.py 文件包含完整 docstring 说明 Base 类用途和继承方式
- [ ] 所有数据库配置参数（pool_size/max_overflow/pool_timeout/pool_recycle）可通过环境变量覆盖默认值

## 边界条件（不做的事）
- 不包含：具体业务表模型定义（User/Product 等，由后续工单实现）
- 不包含：数据库迁移工具集成（Alembic），仅提供基础建表脚本
- 不包含：多数据库支持（仅支持单一 DATABASE_URL 配置的主库）
- 不包含：读写分离配置（主从库路由）
- 不包含：数据库备份和恢复功能
- 暂不支持：数据库连接加密（SSL/TLS）配置
- 超出范围：ORM 查询性能优化（N+1 问题、eager loading 等由业务代码处理）
- 超出范围：数据库监控指标采集（连接池使用率、慢查询统计等）

## 资产需求线索
暂无
