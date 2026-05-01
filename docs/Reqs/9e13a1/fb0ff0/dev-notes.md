# 开发笔记 — Implement budget CRUD API endpoints

> 2026-05-02 01:37 | LLM

## 产出文件
- [backend/app/models/budget.py](/app#repo?file=backend/app/models/budget.py) (4360 chars)
- [backend/app/schemas/budget.py](/app#repo?file=backend/app/schemas/budget.py) (2120 chars)
- [backend/app/api/routes/budgets.py](/app#repo?file=backend/app/api/routes/budgets.py) (8425 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (1719 chars)

## 自测: 自测 6/6 通过 ✅

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 4 个文件 |
| 入口文件 | ✅ | 存在 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 4 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/models/budget.py (新建, 4360 chars)
```
+ from datetime import datetime
+ from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
+ from sqlalchemy.orm import relationship
+ from app.database import Base
+ 
+ 
+ class Budget(Base):
+     __tablename__ = "budgets"
+ 
+     id = Column(Integer, primary_key=True, index=True)
+     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
+     category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
+     amount = Column(Float, nullable=False)
+     period = Column(String(7), nullable=False)  # Format: YYYY-MM
+     spent = Column(Float, default=0.0)
+     created_at = Column(DateTime, default=datetime.utcnow)
+     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
+ 
+     # Relationships
+     user = relationship("User", back_populates="budgets")
+ ... (更多)
```

### backend/app/schemas/budget.py (新建, 2120 chars)
```
+ from pydantic import BaseModel, Field, validator
+ from typing import Optional
+ from datetime import datetime
+ from decimal import Decimal
+ 
+ 
+ class BudgetBase(BaseModel):
+     category_id: int = Field(..., description="分类ID")
+     amount: Decimal = Field(..., gt=0, description="预算金额，必须大于0")
+     period: str = Field(..., description="预算周期，格式：YYYY-MM")
+     
+     @validator('amount')
+     def validate_amount(cls, v):
+         if v <= 0:
+             raise ValueError('预算金额必须大于0')
+         # 保留两位小数
+         return round(v, 2)
+     
+     @validator('period')
+     def validate_period(cls, v):
+ ... (更多)
```

### backend/app/api/routes/budgets.py (新建, 8425 chars)
```
+ from fastapi import APIRouter, Depends, HTTPException, Query
+ from sqlalchemy.orm import Session
+ from typing import List, Optional
+ from datetime import datetime
+ 
+ from app.core.database import get_db
+ from app.core.auth import get_current_user
+ from app.models.user import User
+ from app.models.budget import Budget
+ from app.models.transaction import Transaction
+ from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
+ from sqlalchemy import func, and_
+ 
+ router = APIRouter()
+ 
+ 
+ def validate_period_format(period: str) -> bool:
+     """验证 period 格式 (YYYY-MM)"""
+     try:
+         datetime.strptime(period, "%Y-%m")
+ ... (更多)
```

### backend/app/main.py (修改)
```diff
--- a/backend/app/main.py
+++ b/backend/app/main.py
@@ -3,7 +3,7 @@
 from backend.app.core.config import settings

 from backend.app.core.database import init_db, close_db

 from backend.app.core.middleware import JWTAuthMiddleware

-from backend.app.routers import auth

+from backend.app.routers import auth, budgets

 import logging

 

 # Configure logging

@@ -32,6 +32,7 @@
 

 # Include routers

 app.include_router(auth.router)

+app.include_router(budgets.router)

 

 

 @app.on_event("startup")

```
