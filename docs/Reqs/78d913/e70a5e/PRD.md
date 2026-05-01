# PRD — Design transaction data model and database schema

> 所属需求：收支记录管理（核心功能）

## 用户故事
As a 记账应用用户，I want to 拥有一个结构化的收支记录数据模型和数据库表，So that 系统能够高效存储和查询我的收支记录，为后续的增删改查功能提供数据基础。

## 功能需求
- 数据库表结构：创建 transactions 表，包含以下字段：
  - id: 主键，自增整数
  - user_id: 外键关联用户表，整数，NOT NULL
  - type: 收支类型，枚举值（income/expense），NOT NULL
  - amount: 金额，DECIMAL(10,2)，NOT NULL，≥ 0.01
  - category_id: 外键关联分类表，整数，NOT NULL
  - date: 记账日期，DATE 类型，NOT NULL
  - note: 备注，VARCHAR(500)，可为空
  - payment_method: 支付方式，VARCHAR(50)，可为空（如：现金/支付宝/微信/银行卡）
  - created_at: 创建时间，TIMESTAMP，默认当前时间
  - updated_at: 更新时间，TIMESTAMP，自动更新

- 数据库索引：
  - 主键索引：id
  - 复合索引：(user_id, date DESC) - 优化按用户查询最近记录
  - 单列索引：category_id - 优化分类统计查询
  - 复合索引：(user_id, type, date DESC) - 优化按类型筛选查询

- 数据库迁移文件：
  - 使用 Alembic 创建迁移脚本
  - 文件命名：YYYYMMDD_HHMM_create_transactions_table.py
  - 包含 upgrade() 和 downgrade() 方法

- 数据模型（Python ORM）：
  - 使用 SQLAlchemy 定义 Transaction 模型类
  - 字段类型映射正确（Decimal for amount, Enum for type）
  - 关联关系：belongsTo User, belongsTo Category
  - 数据验证：amount > 0, type in ['income', 'expense']

## 验收标准
- [ ] transactions 表创建成功，包含 10 个字段（id, user_id, type, amount, category_id, date, note, payment_method, created_at, updated_at）
- [ ] user_id 字段设置外键约束，关联 users 表的 id 字段，ON DELETE CASCADE
- [ ] category_id 字段设置外键约束，关联 categories 表的 id 字段，ON DELETE RESTRICT
- [ ] type 字段使用 ENUM 或 CHECK 约束，仅允许 'income' 或 'expense' 两个值
- [ ] amount 字段类型为 DECIMAL(10,2)，支持最大 99,999,999.99，最小 0.01
- [ ] date 字段类型为 DATE，支持 1900-01-01 至 2099-12-31 范围
- [ ] note 字段长度限制 500 字符，超出时数据库拒绝插入
- [ ] created_at 和 updated_at 字段自动填充，created_at 插入时设置，updated_at 每次更新时自动更新
- [ ] 创建 4 个索引：主键索引 + (user_id, date DESC) + (category_id) + (user_id, type, date DESC)
- [ ] 索引创建后，执行 EXPLAIN 查询计划，确认 WHERE user_id=X ORDER BY date DESC 使用复合索引（type=index）
- [ ] Alembic 迁移文件生成成功，文件名格式为 YYYYMMDD_HHMM_create_transactions_table.py
- [ ] 执行 alembic upgrade head 后，数据库中存在 transactions 表且结构正确
- [ ] 执行 alembic downgrade -1 后，transactions 表被删除，数据库恢复到迁移前状态
- [ ] SQLAlchemy 模型类 Transaction 定义完成，包含所有字段属性和关联关系
- [ ] 模型类包含数据验证：尝试插入 amount=0 或 type='invalid' 时抛出 ValidationError
- [ ] 模型类的 __repr__ 方法返回格式：<Transaction(id=X, type=income/expense, amount=Y, date=Z)>
- [ ] 单元测试覆盖率 ≥ 90%：测试模型创建、字段验证、关联查询、索引使用
- [ ] 插入 10000 条测试数据后，按 user_id + date 范围查询（如最近 30 天）耗时 ≤ 50ms

## 边界条件（不做的事）
- 不包含：前端表单组件、API 接口实现（本工单仅负责数据模型和数据库表结构）
- 不包含：分类表（categories）和用户表（users）的创建（假设已存在）
- 不包含：数据迁移脚本（从旧表导入数据）
- 不包含：软删除功能（deleted_at 字段），本期使用物理删除
- 不包含：多币种支持（currency 字段），本期仅支持单一货币
- 不包含：附件上传（如发票图片），本期仅支持文本备注
- 不包含：定时任务（如自动生成周期性账单）
- 暂不支持：分布式数据库（如分库分表），本期使用单库单表
- 超出范围：数据加密存储（amount 字段明文存储）

## 资产需求线索
暂无（本工单为纯后端数据库设计，无 UI 资产需求）
