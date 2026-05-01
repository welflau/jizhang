# 开发笔记 — Create categories database table and migration

> 2026-05-02 01:00 | LLM

## 产出文件
- [backend/migrations/001_create_categories_table.sql](/app#repo?file=backend/migrations/001_create_categories_table.sql) (2041 chars)
- [backend/migrations/__init__.py](/app#repo?file=backend/migrations/__init__.py) (6129 chars)
- [backend/db.py](/app#repo?file=backend/db.py) (7961 chars)
- [backend/models/category.py](/app#repo?file=backend/models/category.py) (1501 chars)
- [backend/main.py](/app#repo?file=backend/main.py) (12573 chars)

## 自测: 自测 6/6 通过 ✅

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 5 个文件 |
| 入口文件 | ✅ | 存在 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 5 个文件已落盘 |

## 代码变更 (Diff)

### backend/migrations/001_create_categories_table.sql (新建, 2041 chars)
```
+ -- Migration: Create categories table
+ -- Created at: 2024-01-01
+ -- Description: Create categories table with user_id, name, type, icon, color, and is_default fields
+ 
+ -- Create categories table
+ CREATE TABLE IF NOT EXISTS categories (
+     id INTEGER PRIMARY KEY AUTOINCREMENT,
+     user_id INTEGER NOT NULL,
+     name VARCHAR(100) NOT NULL,
+     type VARCHAR(10) NOT NULL CHECK(type IN ('income', 'expense')),
+     icon VARCHAR(50),
+     color VARCHAR(20),
+     is_default BOOLEAN DEFAULT 0,
+     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
+ );
+ 
+ -- Create indexes for better query performance
+ CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id);
+ ... (更多)
```

### backend/migrations/__init__.py (新建, 6129 chars)
```
+ """
+ Database migrations package initialization.
+ Provides database migration utilities and version management.
+ """
+ 
+ import os
+ import importlib
+ import logging
+ from typing import List, Optional
+ from datetime import datetime
+ 
+ logger = logging.getLogger(__name__)
+ 
+ 
+ class Migration:
+     """Base migration class"""
+     
+     def __init__(self, version: str, description: str):
+         self.version = version
+         self.description = description
+ ... (更多)
```

### backend/db.py (新建, 7961 chars)
```
+ import sqlite3
+ from contextlib import contextmanager
+ from typing import Optional
+ import os
+ 
+ 
+ DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/finance.db')
+ 
+ 
+ def get_db_connection():
+     """获取数据库连接"""
+     os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
+     conn = sqlite3.connect(DATABASE_PATH)
+     conn.row_factory = sqlite3.Row
+     return conn
+ 
+ 
+ @contextmanager
+ def get_db():
+     """数据库连接上下文管理器"""
+ ... (更多)
```

### backend/models/category.py (新建, 1501 chars)
```
+ from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index
+ from sqlalchemy.orm import relationship
+ from backend.database import Base
+ 
+ 
+ class Category(Base):
+     __tablename__ = "categories"
+ 
+     id = Column(Integer, primary_key=True, index=True)
+     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
+     name = Column(String(50), nullable=False)
+     type = Column(String(10), nullable=False)  # 'income' or 'expense'
+     icon = Column(String(50), nullable=True)
+     color = Column(String(20), nullable=True)
+     is_default = Column(Boolean, default=False, nullable=False)
+ 
+     # Relationships
+     user = relationship("User", back_populates="categories")
+     transactions = relationship("Transaction", back_populates="category", cascade="all, delete-orphan")
+ 
+ ... (更多)
```

### backend/main.py (修改)
```diff
--- a/backend/main.py
+++ b/backend/main.py
@@ -89,6 +89,20 @@
                 FOREIGN KEY (user_id) REFERENCES users(id)

             )

         """)

+        await db.execute("""

+            CREATE TABLE IF NOT EXISTS categories (

+                id INTEGER PRIMARY KEY AUTOINCREMENT,

+                user_id INTEGER NOT NULL,

+                name TEXT NOT NULL,

+                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),

+                icon TEXT,

+                color TEXT,

+                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

+                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

+                FOREIGN KEY (user_id) REFERENCES users(id),

+                UNIQUE(user_id, name, type)

+            )

+        """)

         await db.commit()

 

 @app.on_event("startup")

@@ -315,4 +329,4 @@
 if __name__ == "__main__":

     import uvicorn

     port = int(os.getenv("PORT", 8080))

-    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

+    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
```
