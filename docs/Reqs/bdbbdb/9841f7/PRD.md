# PRD — Create categories database table and migration

> 所属需求：分类管理系统

## 用户故事
As a 记账应用用户，I want to 通过数据库表管理我的收支分类，So that 系统能够持久化存储分类数据并支持高效查询。

## 功能需求
- 创建 categories 表，包含以下字段：
  - id: 主键，自增整数
  - user_id: 外键关联 users 表，NOT NULL
  - name: 分类名称，VARCHAR(50)，NOT NULL
  - type: 分类类型，ENUM('income', 'expense')，NOT NULL
  - icon: 图标标识符，VARCHAR(50)，可为 NULL
  - color: 颜色值（HEX 格式），VARCHAR(7)，默认 '#000000'
  - is_default: 是否为预设分类，BOOLEAN，默认 FALSE
  - created_at: 创建时间戳，DATETIME，默认当前时间
  - updated_at: 更新时间戳，DATETIME，自动更新
- 编写数据库迁移脚本（Alembic/SQLAlchemy）：
  - upgrade() 函数创建表和索引
  - downgrade() 函数回滚删除表
- 添加索引优化查询性能：
  - 复合索引：(user_id, type) 用于按用户和类型筛选
  - 单列索引：user_id 用于用户维度查询
- 添加数据库约束：
  - UNIQUE(user_id, name, type) 防止同一用户创建重复分类
  - FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE

## 验收标准
- [ ] 执行迁移脚本后，数据库中存在 categories 表，包含 9 个字段（id, user_id, name, type, icon, color, is_default, created_at, updated_at）
- [ ] user_id 字段设置为 NOT NULL 且有外键约束指向 users(id)，级联删除生效
- [ ] type 字段仅接受 'income' 或 'expense' 两个值，插入其他值时抛出约束错误
- [ ] name 字段长度限制为 50 字符，超出时插入失败并返回错误信息
- [ ] color 字段默认值为 '#000000'，插入空值时自动填充默认值
- [ ] is_default 字段默认值为 FALSE（或 0）
- [ ] created_at 字段在插入时自动设置为当前时间戳（精确到秒）
- [ ] updated_at 字段在更新记录时自动更新为当前时间戳
- [ ] 复合索引 idx_user_type 存在，覆盖 (user_id, type) 字段
- [ ] 单列索引 idx_user_id 存在，覆盖 user_id 字段
- [ ] UNIQUE 约束 uq_user_name_type 存在，防止同一用户创建相同 name 和 type 的分类
- [ ] 使用 EXPLAIN 查询计划验证：SELECT * FROM categories WHERE user_id=? AND type=? 使用 idx_user_type 索引，type='index'
- [ ] 迁移脚本包含 downgrade() 函数，执行后 categories 表被删除且不影响其他表
- [ ] 迁移脚本文件命名符合 Alembic 规范：YYYYMMDDHHMMSS_create_categories_table.py
- [ ] [假设] 迁移脚本在 backend/alembic/versions/ 目录下，文件编码为 UTF-8

## 边界条件（不做的事）
- 不包含：预设分类数据的初始化（seed data）将在后续工单处理
- 不包含：categories 表的 CRUD API 接口实现
- 不包含：前端分类管理页面开发
- 不包含：图标选择器组件开发
- 暂不支持：分类的软删除（deleted_at 字段），当前使用物理删除
- 暂不支持：分类排序字段（sort_order），后续根据需求添加
- 超出范围：分类使用统计（关联记录数量）的计算逻辑
- 超出范围：分类图标文件的上传和存储

## 资产需求线索
暂无（本工单为纯后端数据库表结构设计，不涉及前端资产）
