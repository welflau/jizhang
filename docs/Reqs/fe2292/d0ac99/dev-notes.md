# 开发笔记 — Design bill query API schema and database indexes

> 2026-05-02 01:22 | LLM

## 产出文件
- [backend/app/models/bill.py](/app#repo?file=backend/app/models/bill.py) (5060 chars)
- [backend/app/models/__init__.py](/app#repo?file=backend/app/models/__init__.py) (2621 chars)
- [backend/alembic/versions/005_create_bills_table.py](/app#repo?file=backend/alembic/versions/005_create_bills_table.py) (6738 chars)
- [backend/app/routers/bills.py](/app#repo?file=backend/app/routers/bills.py) (9237 chars)
- [backend/app/schemas/bill.py](/app#repo?file=backend/app/schemas/bill.py) (5594 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (1314 chars)

## 自测: 自测 6/6 通过 ✅

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 6 个文件 |
| 入口文件 | ✅ | 存在 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 6 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/models/bill.py (新建, 5060 chars)
```
+ from sqlalchemy import Column, Integer, String, Float, DateTime, Index, ForeignKey, Enum as SQLEnum
+ from sqlalchemy.orm import relationship
+ from datetime import datetime
+ import enum
+ 
+ from app.core.database import Base
+ 
+ 
+ class BillType(str, enum.Enum):
+     """账单类型枚举"""
+     INCOME = "income"  # 收入
+     EXPENSE = "expense"  # 支出
+ 
+ 
+ class Bill(Base):
+     """账单模型"""
+     __tablename__ = "bills"
+ 
+     id = Column(Integer, primary_key=True, index=True, comment="账单ID")
+     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
+ ... (更多)
```

### backend/app/models/__init__.py (新建, 2621 chars)
```
+ from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
+ from sqlalchemy.orm import relationship
+ from datetime import datetime
+ from .database import Base
+ 
+ 
+ class User(Base):
+     __tablename__ = "users"
+ 
+     id = Column(Integer, primary_key=True, index=True)
+     username = Column(String(50), unique=True, nullable=False, index=True)
+     email = Column(String(100), unique=True, nullable=False, index=True)
+     hashed_password = Column(String(255), nullable=False)
+     created_at = Column(DateTime, default=datetime.utcnow)
+     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
+ 
+     bills = relationship("Bill", back_populates="user", cascade="all, delete-orphan")
+     categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
+ 
+ 
+ ... (更多)
```

### backend/alembic/versions/005_create_bills_table.py (新建, 6738 chars)
```
+ """create bills table
+ 
+ Revision ID: 005
+ Revises: 004
+ Create Date: 2024-01-01 00:00:00.000000
+ 
+ """
+ from alembic import op
+ import sqlalchemy as sa
+ from sqlalchemy.dialects import postgresql
+ 
+ # revision identifiers, used by Alembic.
+ revision = '005'
+ down_revision = '004'
+ branch_labels = None
+ depends_on = None
+ 
+ 
+ def upgrade() -> None:
+     # Create bills table
+ ... (更多)
```

### backend/app/routers/bills.py (新建, 9237 chars)
```
+ from datetime import datetime
+ from typing import Optional, List
+ from fastapi import APIRouter, Depends, HTTPException, Query
+ from sqlalchemy import and_, or_, func, Index
+ from sqlalchemy.orm import Session
+ from pydantic import BaseModel, Field
+ 
+ from ..database import get_db
+ from ..models import Bill, User
+ from ..auth import get_current_user
+ 
+ router = APIRouter(prefix="/bills", tags=["bills"])
+ 
+ 
+ # Request/Response Schemas
+ class BillBase(BaseModel):
+     amount: float = Field(..., description="金额")
+     category: str = Field(..., description="分类")
+     type: str = Field(..., description="类型：income/expense")
+     description: Optional[str] = Field(None, description="描述")
+ ... (更多)
```

### backend/app/schemas/bill.py (新建, 5594 chars)
```
+ from datetime import datetime
+ from typing import Optional, List
+ from decimal import Decimal
+ from pydantic import BaseModel, Field, validator
+ from enum import Enum
+ 
+ 
+ class BillType(str, Enum):
+     """账单类型枚举"""
+     INCOME = "income"  # 收入
+     EXPENSE = "expense"  # 支出
+ 
+ 
+ class BillBase(BaseModel):
+     """账单基础模型"""
+     amount: Decimal = Field(..., gt=0, description="金额，必须大于0")
+     type: BillType = Field(..., description="账单类型：收入或支出")
+     category_id: int = Field(..., description="分类ID")
+     description: Optional[str] = Field(None, max_length=500, description="账单描述")
+     bill_date: datetime = Field(..., description="账单日期")
+ ... (更多)
```

### backend/app/main.py (修改)
```diff
--- a/backend/app/main.py
+++ b/backend/app/main.py
@@ -2,7 +2,7 @@
 from fastapi.middleware.cors import CORSMiddleware

 from backend.app.core.config import settings

 from backend.app.core.database import init_db

-from backend.app.routers import auth

+from backend.app.routers import auth, bills

 import logging

 

 # Configure logging

@@ -28,6 +28,7 @@
 

 # Include routers

 app.include_router(auth.router)

+app.include_router(bills.router)

 

 

 @app.on_event("startup")

```
