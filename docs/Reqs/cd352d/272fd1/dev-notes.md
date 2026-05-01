# 开发笔记 — Define SQLAlchemy ORM models for core tables

> 2026-05-02 01:11 | LLM

## 产出文件
- [backend/app/models.py](/app#repo?file=backend/app/models.py) (2556 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 1 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 1 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/models.py (新建, 2556 chars)
```
+ from datetime import datetime
+ from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
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
+     id = Column(Integer, primary_key=True, index=True)
+     username = Column(String(50), unique=True, nullable=False, index=True)
+     email = Column(String(100), unique=True, nullable=False, index=True)
+     password_hash = Column(String(255), nullable=False)
+     created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
+ ... (更多)
```
