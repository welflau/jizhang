# PRD — Design transaction data model and database schema

> 所属需求：收支记录管理（核心功能）

## 用户故事
As a 记账应用用户，I want to 有一个稳定可靠的数据存储结构，So that 我的每一笔收支记录都能被准确保存、快速查询，并且支持后续的统计分析功能。

## 功能需求
- 数据库表结构设计：创建 transactions 表，包含 id（主键）、user_id（外键）、type（收入/支出枚举）、amount（金额，精确到分）、category_id（外键）、date（记账日期）、note（备注）、payment_method（支付方式）、created_at（创建时间）、updated_at（更新时间）
- 字段约束：amount 必须为正数，type 只能是 'income' 或 'expense'，user_id 和 category_id 必须关联到已存在的用户和分类
- 索引优化：为 user_id、date、type、category_id 创建复合索引，支持按用户、时间范围、类型快速筛选
- 数据库迁移：使用 Alembic 创建迁移文件，支持版本管理和回滚
- 数据完整性：设置外键约束，确保 user_id 和 category_id 的引用完整性

## 验收标准
- [ ] transactions 表创建成功，包含 10 个字段：id, user_id, type, amount, category_id, date, note, payment_method, created_at, updated_at
- [ ] id 字段为自增主键，user_id 和 category_id 设置外键约束并关联到对应表
- [ ] type 字段使用 ENUM 或 CHECK 约束，只允许 'income' 和 'expense' 两个值
- [ ] amount 字段类型为 DECIMAL(15,2)，约束 > 0，支持最大 13 位整数 + 2 位小数
- [ ] date 字段类型为 DATE，默认值为当前日期
- [ ] note 字段类型为 VARCHAR(500)，允许为空
- [ ] payment_method 字段类型为 VARCHAR(50)，允许为空
- [ ] created_at 和 updated_at 字段类型为 TIMESTAMP，created_at 默认当前时间，updated_at 自动更新
- [ ] 创建复合索引 idx_user_date_type，包含 (user_id, date DESC, type)，查询单用户某月记录时扫描行数 ≤ 实际记录数的 110%
- [ ] 创建单列索引 idx_category，包含 category_id，支持按分类统计
- [ ] Alembic 迁移文件生成在 backend/alembic/versions/ 目录，文件名格式为 {revision}_create_transactions_table.py
- [ ] 执行 alembic upgrade head 后，数据库中存在 transactions 表且结构符合设计
- [ ] 执行 alembic downgrade -1 后，transactions 表被删除，数据库恢复到迁移前状态
- [ ] 插入测试数据：user_id=1, type='expense', amount=100.50, category_id=1, date='2025-01-15'，插入成功且 created_at 自动填充当前时间戳
- [ ] 尝试插入 amount=-50 的记录时，数据库返回约束错误，拒绝插入
- [ ] 尝试插入 type='other' 的记录时，数据库返回枚举/CHECK 约束错误
- [ ] 尝试插入不存在的 user_id=9999 时，数据库返回外键约束错误
- [ ] 查询 SELECT * FROM transactions WHERE user_id=1 AND date BETWEEN '2025-01-01' AND '2025-01-31' 时，EXPLAIN 显示使用 idx_user_date_type 索引

## 边界条件（不做的事）
- 不包含：ORM 模型定义（由后续工单实现）
- 不包含：API 接口开发（由后续工单实现）
- 不包含：前端表单和列表组件（由后续工单实现）
- 暂不支持：软删除（deleted_at 字段），当前为物理删除
- 暂不支持：多币种（currency 字段），默认所有金额为人民币
- 暂不支持：附件上传（attachment_url 字段），仅支持文本备注
- 超出范围：数据备份和恢复策略（由运维工单处理）
- 超出范围：分库分表设计（当前单表支持百万级记录）

## 资产需求线索
暂无
