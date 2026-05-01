# PRD — Create categories database table and migration

> 所属需求：分类管理系统

## 用户故事
As a 记账应用用户，I want to 通过数据库表存储和管理我的收支分类，So that 系统能够持久化保存分类数据，并支持后续的增删改查操作。

## 功能需求
- 创建 categories 表，包含以下字段：
  - id: 主键，自增整数
  - user_id: 外键关联用户表，整数类型，NOT NULL
  - name: 分类名称，字符串类型（最大长度 50），NOT NULL
  - type: 分类类型，枚举值（'income' 或 'expense'），NOT NULL
  - icon: 图标标识符，字符串类型（最大长度 50），可为 NULL
  - color: 颜色值，字符串类型（格式 #RRGGBB，长度 7），可为 NULL
  - is_default: 是否为预设分类，布尔类型，默认 FALSE
  - created_at: 创建时间戳，自动生成
  - updated_at: 更新时间戳，自动更新

- 编写数据库迁移脚本（Alembic migration）：
  - 包含 upgrade() 和 downgrade() 函数
  - 添加表结构定义
  - 添加索引优化

- 添加以下索引：
  - idx_categories_user_id: 单列索引（user_id）
  - idx_categories_user_type: 复合索引（user_id, type）
  - idx_categories_user_default: 复合索引（user_id, is_default）

- 添加外键约束：
  - user_id REFERENCES users(id) ON DELETE CASCADE

- 添加唯一约束：
  - UNIQUE(user_id, name, type) - 同一用户下同类型分类名称不可重复

## 验收标准
- [ ] 执行迁移脚本后，数据库中存在 categories 表，包含 9 个字段（id, user_id, name, type, icon, color, is_default, created_at, updated_at）
- [ ] user_id 字段设置为 NOT NULL 且存在外键约束指向 users 表
- [ ] name 字段最大长度为 50 字符，NOT NULL
- [ ] type 字段仅接受 'income' 或 'expense' 两个枚举值（通过 CHECK 约束或 ENUM 类型实现）
- [ ] icon 字段最大长度为 50 字符，允许 NULL
- [ ] color 字段长度为 7 字符（格式 #RRGGBB），允许 NULL
- [ ] is_default 字段默认值为 FALSE
- [ ] created_at 和 updated_at 字段自动记录时间戳（created_at 在插入时生成，updated_at 在更新时自动更新）
- [ ] 存在索引 idx_categories_user_id，查询 `SELECT * FROM categories WHERE user_id = ?` 时使用该索引（通过 EXPLAIN QUERY PLAN 验证）
- [ ] 存在复合索引 idx_categories_user_type，查询 `SELECT * FROM categories WHERE user_id = ? AND type = ?` 时使用该索引
- [ ] 存在复合索引 idx_categories_user_default，查询 `SELECT * FROM categories WHERE user_id = ? AND is_default = TRUE` 时使用该索引
- [ ] 存在唯一约束 UNIQUE(user_id, name, type)，插入重复分类名称时抛出 IntegrityError
- [ ] 删除 users 表中的用户记录时，该用户的所有 categories 记录自动级联删除（ON DELETE CASCADE）
- [ ] 迁移脚本包含 downgrade() 函数，执行后能完全回滚表结构（删除表和索引）
- [ ] 迁移脚本文件命名符合 Alembic 规范：`YYYYMMDDHHMMSS_create_categories_table.py`
- [ ] 迁移脚本在 PostgreSQL 和 SQLite 两种数据库上均能成功执行（[假设] 项目支持多数据库）

## 边界条件（不做的事）
- 不包含：预设分类数据的初始化（seed data）- 将在后续工单中实现
- 不包含：SQLAlchemy ORM 模型定义 - 将在后续工单中实现
- 不包含：分类的 CRUD API 接口 - 将在后续工单中实现
- 不包含：分类图标和颜色的验证逻辑 - 将在应用层实现
- 暂不支持：分类的软删除（deleted_at 字段）- 当前版本使用物理删除
- 暂不支持：分类的排序字段（sort_order）- 后续根据需求添加
- 暂不支持：分类的多语言支持 - 当前仅支持单一语言
- 超出范围：分类的层级结构（父子分类）- 当前版本仅支持扁平结构

## 资产需求线索
暂无
