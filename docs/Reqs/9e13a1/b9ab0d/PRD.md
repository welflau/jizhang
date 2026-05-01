# PRD — Create budgets table schema and migration

> 所属需求：预算管理功能

## 用户故事
As a 用户，I want to 设置月度预算并实时查看支出进度，So that 我能有效控制开支并在超支前收到预警。

## 功能需求
- 预算设置：支持设置总预算或按分类设置预算，指定月份周期（YYYY-MM 格式）
- 数据表设计：budgets 表包含 id（主键）、user_id（外键关联 users）、category_id（可选外键关联 categories）、amount（预算金额，DECIMAL 类型）、period（预算周期 VARCHAR）、created_at（创建时间 TIMESTAMP）
- 索引优化：为 (user_id, period) 创建联合索引，为 category_id 创建单列索引
- 数据库迁移：编写 Alembic/SQLAlchemy 迁移脚本，包含表创建、外键约束、索引创建、回滚逻辑

## 验收标准
- [ ] budgets 表创建成功，包含 6 个字段：id (INTEGER PRIMARY KEY AUTOINCREMENT)、user_id (INTEGER NOT NULL)、category_id (INTEGER NULL)、amount (DECIMAL(10,2) NOT NULL)、period (VARCHAR(7) NOT NULL)、created_at (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
- [ ] user_id 外键约束指向 users(id)，设置 ON DELETE CASCADE
- [ ] category_id 外键约束指向 categories(id)，设置 ON DELETE SET NULL
- [ ] 创建联合索引 idx_budgets_user_period ON budgets(user_id, period)，查询 EXPLAIN 显示使用该索引
- [ ] 创建单列索引 idx_budgets_category ON budgets(category_id)
- [ ] amount 字段添加 CHECK 约束：amount > 0
- [ ] period 字段添加 CHECK 约束：period REGEXP '^[0-9]{4}-[0-9]{2}$'（或数据库对应的格式校验）
- [ ] 迁移脚本包含 upgrade() 和 downgrade() 函数，downgrade 能完整回滚表和索引
- [ ] 执行 alembic upgrade head 后，数据库中存在 budgets 表且结构符合设计
- [ ] 执行 alembic downgrade -1 后，budgets 表及相关索引被完全删除
- [ ] 插入测试数据：user_id=1, amount=5000.00, period='2026-05' 成功，查询耗时 < 10ms（有索引）
- [ ] 插入非法数据：amount=-100 或 period='202605' 时抛出约束错误

## 边界条件（不做的事）
- 不包含：预算进度计算逻辑（由后续工单实现）
- 不包含：预算超支预警功能（由后续工单实现）
- 不包含：前端表单和可视化组件（由后续工单实现）
- 暂不支持：周预算或自定义周期（仅支持月度 YYYY-MM）
- 暂不支持：预算模板或预算复制功能
- 超出范围：预算分析报表、预算与实际支出对比图表

## 资产需求线索
暂无
