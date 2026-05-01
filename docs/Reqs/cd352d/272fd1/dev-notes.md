# 开发笔记 — Define SQLAlchemy ORM models for core tables

> 2026-05-02 01:06 | LLM

## 产出文件
- [backend/models/__init__.py](/app#repo?file=backend/models/__init__.py) (339 chars)
- [backend/models/user.py](/app#repo?file=backend/models/user.py) (2762 chars)
- [backend/models/category.py](/app#repo?file=backend/models/category.py) (3120 chars)
- [backend/models/transaction.py](/app#repo?file=backend/models/transaction.py) (3828 chars)
- [backend/models/payment_method.py](/app#repo?file=backend/models/payment_method.py) (2557 chars)
- [backend/models/base.py](/app#repo?file=backend/models/base.py) (278 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 6 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 6 个文件已落盘 |

## 代码变更 (Diff)

### backend/models/__init__.py (新建, 339 chars)
```
+ """SQLAlchemy ORM models package.
+ 
+ Exports all models for easy import:
+     from models import User, Category, Transaction, PaymentMethod
+ """
+ 
+ from .user import User
+ from .category import Category
+ from .transaction import Transaction
+ from .payment_method import PaymentMethod
+ 
+ __all__ = ["User", "Category", "Transaction", "PaymentMethod"]
+ 
```

### backend/models/user.py (新建, 2762 chars)
```
+ """User model for authentication and user management.
+ 
+ Fields:
+     - id: Primary key
+     - username: Unique login identifier (3-30 chars, indexed for fast lookup)
+     - email: Unique email address (indexed, validated format)
+     - password_hash: Bcrypt hashed password (255 chars to accommodate hash output)
+     - created_at: Account creation timestamp
+     - updated_at: Last modification timestamp
+ 
+ Relationships:
+     - categories: User's custom income/expense categories
+     - transactions: User's financial transaction records
+     - payment_methods: User's payment method configurations
+ """
+ 
+ from sqlalchemy import Column, Integer, String, DateTime, Index
+ from sqlalchemy.orm import relationship
+ from sqlalchemy.sql import func
+ from .base import Base
+ ... (更多)
```

### backend/models/category.py (新建, 3120 chars)
```
+ """Category model for income/expense classification.
+ 
+ Fields:
+     - id: Primary key
+     - user_id: Foreign key to users table (CASCADE delete)
+     - name: Category display name (max 50 chars)
+     - type: Enum('income', 'expense') for transaction type
+     - icon: Optional icon identifier (e.g., 'food', 'transport')
+     - color: Optional hex color code for UI display
+     - created_at: Category creation timestamp
+     - updated_at: Last modification timestamp
+ 
+ Constraints:
+     - Unique(user_id, name): Prevent duplicate category names per user
+     - CHECK(type IN ('income', 'expense')): Enforce valid type values
+ 
+ Relationships:
+     - user: Owner of this category
+     - transactions: Transactions tagged with this category
+ """
+ ... (更多)
```

### backend/models/transaction.py (新建, 3828 chars)
```
+ """Transaction model for financial record tracking.
+ 
+ Fields:
+     - id: Primary key
+     - user_id: Foreign key to users table (CASCADE delete)
+     - category_id: Foreign key to categories table (SET NULL on delete)
+     - payment_method_id: Foreign key to payment_methods table (SET NULL on delete)
+     - amount: Decimal(10,2) for precise currency storage
+     - date: Transaction date (indexed for time-range queries)
+     - description: Optional transaction note (max 500 chars)
+     - created_at: Record creation timestamp
+     - updated_at: Last modification timestamp
+ 
+ Constraints:
+     - amount > 0: Enforce positive transaction amounts
+     - date <= today: Prevent future-dated transactions
+ 
+ Relationships:
+     - user: Owner of this transaction
+     - category: Classification category (nullable if category deleted)
+ ... (更多)
```

### backend/models/payment_method.py (新建, 2557 chars)
```
+ """PaymentMethod model for payment method management.
+ 
+ Fields:
+     - id: Primary key
+     - user_id: Foreign key to users table (CASCADE delete)
+     - name: Payment method display name (max 50 chars)
+     - type: Payment type (e.g., 'cash', 'credit_card', 'debit_card', 'digital_wallet')
+     - created_at: Method creation timestamp
+     - updated_at: Last modification timestamp
+ 
+ Constraints:
+     - Unique(user_id, name): Prevent duplicate payment method names per user
+ 
+ Relationships:
+     - user: Owner of this payment method
+     - transactions: Transactions using this payment method
+ """
+ 
+ from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Index
+ from sqlalchemy.orm import relationship
+ ... (更多)
```

### backend/models/base.py (新建, 278 chars)
```
+ """SQLAlchemy declarative base for all models.
+ 
+ Provides:
+     - Base: Declarative base class for all ORM models
+     - Shared configuration for table naming conventions
+ """
+ 
+ from sqlalchemy.orm import declarative_base
+ 
+ # Declarative base for all models
+ Base = declarative_base()
+ 
```
