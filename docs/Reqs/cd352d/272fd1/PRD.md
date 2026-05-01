# PRD — Define SQLAlchemy ORM models for core tables

> 所属需求：数据库设计与初始化

## 用户故事
As a backend developer, I want to define SQLAlchemy ORM models for core database tables, So that the application can interact with PostgreSQL database using type-safe Python objects and maintain data integrity through proper relationships and constraints.

## 功能需求
- User Model: Define User table with fields id (UUID primary key), username (unique, max 50 chars), email (unique, max 100 chars), password_hash (max 255 chars), created_at (timestamp with timezone), updated_at (timestamp with timezone)
- Category Model: Define Category table with fields id (UUID primary key), name (max 50 chars), type (enum: 'income'/'expense'), icon (max 50 chars, nullable), color (max 20 chars, nullable), user_id (UUID foreign key to users.id, nullable for system categories), created_at (timestamp with timezone)
- Transaction Model: Define Transaction table with fields id (UUID primary key), user_id (UUID foreign key to users.id, not null), category_id (UUID foreign key to categories.id, not null), amount (Numeric(12,2), not null), date (Date, not null), description (Text, nullable), payment_method_id (UUID foreign key to payment_methods.id, nullable), created_at (timestamp with timezone), updated_at (timestamp with timezone)
- PaymentMethod Model: Define PaymentMethod table with fields id (UUID primary key), user_id (UUID foreign key to users.id, not null), name (max 50 chars, not null), type (max 30 chars, nullable), created_at (timestamp with timezone)
- Relationship Definitions: User.categories (one-to-many), User.transactions (one-to-many), User.payment_methods (one-to-many), Category.transactions (one-to-many), Transaction.user (many-to-one), Transaction.category (many-to-one), Transaction.payment_method (many-to-one)
- Base Model: Create abstract BaseModel with common fields (id, created_at, updated_at) and timestamp auto-update mixin
- Index Hints: Add __table_args__ comments for indexes on user_id, date, category_id (actual index creation in migration script)

## 验收标准
- [ ] 创建 backend/models/__init__.py 文件，导出所有模型类（User, Category, Transaction, PaymentMethod）
- [ ] 创建 backend/models/base.py，定义 BaseModel 抽象类，包含 id (UUID, primary_key=True, default=uuid4), created_at (DateTime(timezone=True), server_default=func.now()), updated_at (DateTime(timezone=True), onupdate=func.now())
- [ ] 创建 backend/models/user.py，User 模型继承 BaseModel，包含 username (String(50), unique=True, nullable=False), email (String(100), unique=True, nullable=False), password_hash (String(255), nullable=False)
- [ ] User 模型定义反向引用：categories = relationship('Category', back_populates='user'), transactions = relationship('Transaction', back_populates='user'), payment_methods = relationship('PaymentMethod', back_populates='user')
- [ ] 创建 backend/models/category.py，Category 模型包含 name (String(50), nullable=False), type (Enum('income', 'expense', name='category_type'), nullable=False), icon (String(50)), color (String(20)), user_id (UUID, ForeignKey('users.id', ondelete='CASCADE'))
- [ ] Category 模型定义关系：user = relationship('User', back_populates='categories'), transactions = relationship('Transaction', back_populates='category')
- [ ] 创建 backend/models/transaction.py，Transaction 模型包含 user_id (UUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False), category_id (UUID, ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False), amount (Numeric(12, 2), nullable=False), date (Date, nullable=False), description (Text), payment_method_id (UUID, ForeignKey('payment_methods.id', ondelete='SET NULL'))
- [ ] Transaction 模型定义关系：user = relationship('User', back_populates='transactions'), category = relationship('Category', back_populates='transactions'), payment_method = relationship('PaymentMethod', back_populates='transactions')
- [ ] Transaction 模型 __table_args__ 包含注释：Index hint for (user_id, date DESC), Index hint for (category_id)
- [ ] 创建 backend/models/payment_method.py，PaymentMethod 模型包含 user_id (UUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False), name (String(50), nullable=False), type (String(30))
- [ ] PaymentMethod 模型定义关系：user = relationship('User', back_populates='payment_methods'), transactions = relationship('Transaction', back_populates='payment_method')
- [ ] 所有外键约束明确指定 ondelete 行为（CASCADE/RESTRICT/SET NULL）
- [ ] 所有模型类包含 __tablename__ 属性（users, categories, transactions, payment_methods）
- [ ] 所有字段的 nullable 属性明确设置（True/False），无默认依赖
- [ ] 所有字符串字段指定最大长度（String(N)）
- [ ] 金额字段使用 Numeric(12, 2) 类型，精度固定为 2 位小数
- [ ] 时间戳字段使用 DateTime(timezone=True)，支持时区
- [ ] 枚举类型使用 SQLAlchemy Enum，指定 name 参数（避免数据库枚举类型冲突）
- [ ] 所有模型文件顶部包含 docstring，说明表用途和主要字段
- [ ] 代码通过 flake8 检查，无 E501（行长度）、E302（空行）等错误
- [ ] 所有文件使用 UTF-8 编码，Unix 换行符（LF）

## 边界条件（不做的事）
- 不包含：数据库迁移脚本（Alembic migration 在后续工单）
- 不包含：索引的实际创建语句（仅在模型中添加 __table_args__ 注释提示）
- 不包含：默认数据种子（seed data 在后续工单）
- 不包含：数据库连接配置（database.py 在后续工单）
- 不包含：模型的业务逻辑方法（如密码验证、金额计算等，在 service 层实现）
- 不包含：Pydantic schema 定义（API 输入输出模型在后续工单）
- 暂不支持：软删除（deleted_at 字段），当前使用物理删除
- 暂不支持：多租户隔离（tenant_id），当前单租户设计
- 暂不支持：审计日志表（audit_logs），当前仅记录 created_at/updated_at
- 超出范围：数据库性能测试、查询优化分析
- 超出范围：ORM 查询示例代码（在 API 层工单实现）

## 资产需求线索
暂无
