# PRD — Create budgets table schema and migration

> 所属需求：预算管理功能

## 用户故事
As a 记账应用用户，I want to 设置月度预算并查看使用进度，So that 我可以控制支出避免超支，并通过历史记录分析消费习惯。

## 功能需求
- 数据表设计：创建 budgets 表，包含 id (主键)、user_id (外键关联 users 表)、category_id (可选外键关联 categories 表)、amount (预算金额，DECIMAL 类型)、period (预算周期，格式 YYYY-MM，VARCHAR 类型)、created_at (创建时间，TIMESTAMP 类型)
- 索引优化：为 user_id 和 period 字段创建联合索引，支持按用户和月份快速查询
- 外键约束：user_id 关联 users(id) ON DELETE CASCADE，category_id 关联 categories(id) ON DELETE SET NULL
- 数据库迁移：编写 Alembic/SQLAlchemy 迁移脚本，支持版本管理和回滚
- 字段约束：amount > 0，period 格式校验（正则 ^\d{4}-\d{2}$），user_id NOT NULL

## 验收标准
- [ ] budgets 表创建成功，包含所有必需字段（id, user_id, category_id, amount, period, created_at）
- [ ] user_id 字段设置为 NOT NULL，并添加外键约束关联 users(id)，级联删除策略为 CASCADE
- [ ] category_id 字段允许 NULL，外键约束关联 categories(id)，删除分类时预算记录的 category_id 自动设为 NULL
- [ ] amount 字段类型为 DECIMAL(10,2)，添加 CHECK 约束确保 amount > 0
- [ ] period 字段类型为 VARCHAR(7)，添加 CHECK 约束验证格式为 YYYY-MM（如 2025-01）
- [ ] created_at 字段类型为 TIMESTAMP，默认值为当前时间（DEFAULT CURRENT_TIMESTAMP）
- [ ] 创建联合索引 idx_budgets_user_period (user_id, period)，查询单用户单月预算时执行计划显示使用该索引
- [ ] 迁移脚本包含 upgrade() 和 downgrade() 函数，执行 downgrade 后表被正确删除
- [ ] 插入测试数据（user_id=1, category_id=NULL, amount=5000.00, period='2025-05'）成功，查询返回正确记录
- [ ] 插入无效数据（amount=-100 或 period='2025-13'）时抛出约束错误
- [ ] 删除关联用户后，该用户的所有预算记录自动删除（验证 CASCADE 生效）
- [ ] 删除关联分类后，预算记录的 category_id 字段变为 NULL（验证 SET NULL 生效）

## 边界条件（不做的事）
- 不包含：预算使用进度计算逻辑（由后续工单实现）
- 不包含：预算超支预警功能（由后续工单实现）
- 不包含：前端表单和 API 接口（由后续工单实现）
- 暂不支持：周预算或年预算（仅支持月度预算，period 格式固定为 YYYY-MM）
- 暂不支持：多币种预算（amount 字段无货币类型标识）
- 超出范围：预算模板功能（快速复制上月预算）
- 超出范围：预算分享功能（多用户协同预算）

## 资产需求线索
暂无
