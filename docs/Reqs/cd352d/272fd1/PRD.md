# PRD — Define SQLAlchemy ORM models for core tables

> 所属需求：数据库设计与初始化

## 用户故事
作为用户，我需要 Define SQLAlchemy ORM models for core tables

## 功能需求
- 创建 SQLAlchemy 模型定义文件，包含：
- User 模型（用户表）：id, username, email, password_hash, created_at 等字段
- Category 模型（分类表）：id, name, type (income/expense), icon, color 等字段
- Transaction 模型（交易记录表）：id, user_id, category_id, amount, date, description, payment_method_id 等字段
- PaymentMethod 模型（支付方式表）：id, user_id, name, type 等字段

定义模型间关系（外键、反向引用），确保字段类型、长度、nullable 等属性符合业务需求。

## 验收标准
- 功能可正常使用（待细化）

## 边界条件（不做的事）
- 暂无特殊限制

## 资产需求线索
暂无
