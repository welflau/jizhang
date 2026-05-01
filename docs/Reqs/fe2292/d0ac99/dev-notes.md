# 开发笔记 — Design bill query API schema and database indexes

> 2026-05-02 01:09 | LLM

## 产出文件
- [backend/app/models/bill.py](/app#repo?file=backend/app/models/bill.py) (3005 chars)
- [backend/alembic/versions/003_add_bill_indexes.py](/app#repo?file=backend/alembic/versions/003_add_bill_indexes.py) (2482 chars)
- [backend/app/routes/bills.py](/app#repo?file=backend/app/routes/bills.py) (13954 chars)
- [backend/app/schemas/bill.py](/app#repo?file=backend/app/schemas/bill.py) (5643 chars)
- [backend/app.py](/app#repo?file=backend/app.py) (2895 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 5 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 5 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/models/bill.py (新建, 3005 chars)
```
+ from datetime import datetime
+ from typing import Optional
+ from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Index, Text
+ from sqlalchemy.orm import relationship
+ import enum
+ 
+ from app.db.base_class import Base
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
+ ... (更多)
```

### backend/alembic/versions/003_add_bill_indexes.py (新建, 2482 chars)
```
+ """add bill indexes
+ 
+ Revision ID: 003
+ Revises: 002
+ Create Date: 2024-01-01 00:00:00.000000
+ 
+ """
+ from alembic import op
+ import sqlalchemy as sa
+ 
+ 
+ # revision identifiers, used by Alembic.
+ revision = '003'
+ down_revision = '002'
+ branch_labels = None
+ depends_on = None
+ 
+ 
+ def upgrade():
+     # 为账单表添加索引以优化查询性能
+ ... (更多)
```

### backend/app/routes/bills.py (新建, 13954 chars)
```
+ from datetime import datetime
+ from typing import Optional, List
+ from fastapi import APIRouter, Depends, HTTPException, Query
+ from sqlalchemy import and_, or_, desc, asc
+ from sqlalchemy.orm import Session
+ from pydantic import BaseModel, Field
+ 
+ from app.database import get_db
+ from app.models.bill import Bill
+ from app.models.category import Category
+ from app.auth import get_current_user
+ 
+ router = APIRouter(prefix="/bills", tags=["bills"])
+ 
+ 
+ # Request/Response Schemas
+ class BillCreate(BaseModel):
+     type: str = Field(..., description="账单类型: income 或 expense")
+     amount: float = Field(..., gt=0, description="金额，必须大于0")
+     category_id: int = Field(..., description="分类ID")
+ ... (更多)
```

### backend/app/schemas/bill.py (新建, 5643 chars)
```
+ from datetime import datetime
+ from decimal import Decimal
+ from typing import Optional, List
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
+     bill_type: BillType = Field(..., description="账单类型：收入或支出")
+     category_id: int = Field(..., description="分类ID")
+     description: Optional[str] = Field(None, max_length=500, description="账单描述")
+     bill_date: datetime = Field(..., description="账单日期")
+ ... (更多)
```

### backend/app.py (修改)
```diff
--- a/backend/app.py
+++ b/backend/app.py
@@ -6,6 +6,7 @@
 from backend.api.export import export_bp

 from backend.api.import_data import import_bp

 from backend.api.clear import clear_bp

+from backend.api.bills import bills_bp

 

 # Configure logging

 logging.basicConfig(

@@ -21,6 +22,7 @@
 app.register_blueprint(export_bp)

 app.register_blueprint(import_bp)

 app.register_blueprint(clear_bp)

+app.register_blueprint(bills_bp)

 

 # Initialize database

 init_db()

@@ -106,4 +108,4 @@
 

 if __name__ == '__main__':

     port = int(os.getenv('PORT', 8080))

-    app.run(host='0.0.0.0', port=port, debug=True)

+    app.run(host='0.0.0.0', port=port, debug=True)
```
