# 开发笔记 — Define SQLAlchemy ORM models for core tables

> 2026-05-02 01:14 | LLM

## 产出文件
- [backend/app/models/__init__.py](/app#repo?file=backend/app/models/__init__.py) (3266 chars)
- [backend/app/models/user.py](/app#repo?file=backend/app/models/user.py) (2643 chars)
- [backend/app/models/category.py](/app#repo?file=backend/app/models/category.py) (1469 chars)
- [backend/app/models/transaction.py](/app#repo?file=backend/app/models/transaction.py) (2189 chars)
- [backend/app/models/payment_method.py](/app#repo?file=backend/app/models/payment_method.py) (1733 chars)
- [backend/app/models/base.py](/app#repo?file=backend/app/models/base.py) (3230 chars)

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

### backend/app/models/__init__.py (新建, 3266 chars)
```
+ from datetime import datetime
+ from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
+ from sqlalchemy.orm import relationship
+ from sqlalchemy.ext.declarative import declarative_base
+ import enum
+ 
+ Base = declarative_base()
+ 
+ 
+ class TransactionType(enum.Enum):
+     income = "income"
+     expense = "expense"
+ 
+ 
+ class User(Base):
+     __tablename__ = "users"
+ 
+     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
+     username = Column(String(50), unique=True, nullable=False, index=True)
+     email = Column(String(100), unique=True, nullable=False, index=True)
+ ... (更多)
```

### backend/app/models/user.py (新建, 2643 chars)
```
+ from datetime import datetime
+ from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum as SQLEnum
+ from sqlalchemy.orm import relationship
+ from app.database import Base
+ import enum
+ 
+ 
+ class TransactionType(str, enum.Enum):
+     INCOME = "income"
+     EXPENSE = "expense"
+ 
+ 
+ class User(Base):
+     __tablename__ = "users"
+ 
+     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
+     username = Column(String(50), unique=True, nullable=False, index=True)
+     email = Column(String(100), unique=True, nullable=False, index=True)
+     password_hash = Column(String(255), nullable=False)
+     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
+ ... (更多)
```

### backend/app/models/category.py (新建, 1469 chars)
```
+ from datetime import datetime
+ from sqlalchemy import Column, Integer, String, DateTime
+ from sqlalchemy.orm import relationship
+ from app.database import Base
+ 
+ 
+ class Category(Base):
+     """分类模型"""
+     __tablename__ = "categories"
+ 
+     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
+     name = Column(String(50), nullable=False, comment="分类名称")
+     type = Column(String(10), nullable=False, comment="分类类型: income/expense")
+     icon = Column(String(50), nullable=True, comment="图标名称")
+     color = Column(String(20), nullable=True, comment="颜色代码")
+     user_id = Column(Integer, nullable=True, comment="用户ID，NULL表示系统默认分类")
+     created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
+     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
+ 
+     # 关系定义
+ ... (更多)
```

### backend/app/models/transaction.py (新建, 2189 chars)
```
+ from datetime import datetime
+ from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum
+ from sqlalchemy.orm import relationship
+ from app.database import Base
+ import enum
+ 
+ 
+ class TransactionType(enum.Enum):
+     """交易类型枚举"""
+     INCOME = "income"
+     EXPENSE = "expense"
+ 
+ 
+ class Transaction(Base):
+     """交易记录模型"""
+     __tablename__ = "transactions"
+ 
+     id = Column(Integer, primary_key=True, index=True, comment="交易记录ID")
+     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID")
+     category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True, comment="分类ID")
+ ... (更多)
```

### backend/app/models/payment_method.py (新建, 1733 chars)
```
+ from datetime import datetime
+ from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
+ from sqlalchemy.orm import relationship
+ from app.database import Base
+ 
+ 
+ class PaymentMethod(Base):
+     """支付方式模型"""
+     __tablename__ = "payment_methods"
+ 
+     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
+     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
+     name = Column(String(50), nullable=False, comment="支付方式名称，如：现金、支付宝、微信、银行卡等")
+     icon = Column(String(50), default="wallet", comment="图标标识")
+     color = Column(String(20), default="#1890ff", comment="颜色标识")
+     is_active = Column(Boolean, default=True, comment="是否启用")
+     sort_order = Column(Integer, default=0, comment="排序顺序")
+     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
+     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
+ 
+ ... (更多)
```

### backend/app/models/base.py (新建, 3230 chars)
```
+ from datetime import datetime
+ from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
+ from sqlalchemy.orm import relationship
+ from sqlalchemy.ext.declarative import declarative_base
+ import enum
+ 
+ Base = declarative_base()
+ 
+ 
+ class TransactionType(enum.Enum):
+     """交易类型枚举"""
+     INCOME = "income"
+     EXPENSE = "expense"
+ 
+ 
+ class User(Base):
+     """用户模型"""
+     __tablename__ = "users"
+ 
+     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
+ ... (更多)
```
