# 开发笔记 — Create categories database table and migration

> 2026-05-02 00:59 | LLM

## 产出文件
- [backend/migrations/001_create_categories_table.sql](/app#repo?file=backend/migrations/001_create_categories_table.sql) (2019 chars)
- [backend/migrations/__init__.py](/app#repo?file=backend/migrations/__init__.py) (5852 chars)
- [backend/database.py](/app#repo?file=backend/database.py) (6200 chars)
- [backend/models.py](/app#repo?file=backend/models.py) (5948 chars)
- [backend/main.py](/app#repo?file=backend/main.py) (12573 chars)

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

### backend/migrations/001_create_categories_table.sql (新建, 2019 chars)
```
+ -- Migration: Create categories table
+ -- Description: Creates the categories table for storing income and expense categories
+ 
+ -- Create categories table
+ CREATE TABLE IF NOT EXISTS categories (
+     id SERIAL PRIMARY KEY,
+     user_id INTEGER NOT NULL,
+     name VARCHAR(100) NOT NULL,
+     type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
+     icon VARCHAR(50),
+     color VARCHAR(20),
+     is_default BOOLEAN DEFAULT FALSE,
+     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
+     updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
+ );
+ 
+ -- Create indexes for performance optimization
+ CREATE INDEX idx_categories_user_id ON categories(user_id);
+ CREATE INDEX idx_categories_type ON categories(type);
+ CREATE INDEX idx_categories_user_type ON categories(user_id, type);
+ ... (更多)
```

### backend/migrations/__init__.py (新建, 5852 chars)
```
+ """
+ Database migrations package initialization.
+ """
+ 
+ import os
+ import importlib.util
+ from typing import List, Optional
+ from datetime import datetime
+ 
+ 
+ class Migration:
+     """Base migration class."""
+     
+     def __init__(self, version: str, description: str):
+         self.version = version
+         self.description = description
+         self.applied_at: Optional[datetime] = None
+     
+     def up(self, cursor):
+         """Apply migration."""
+ ... (更多)
```

### backend/database.py (新建, 6200 chars)
```
+ backend/database.py
+ 
+ import os
+ from sqlalchemy import create_engine, Column, Integer, String, Boolean, Enum, Index
+ from sqlalchemy.ext.declarative import declarative_base
+ from sqlalchemy.orm import sessionmaker
+ from sqlalchemy.pool import StaticPool
+ import enum
+ 
+ # 数据库配置
+ DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finance_tracker.db")
+ 
+ # 创建数据库引擎
+ if DATABASE_URL.startswith("sqlite"):
+     engine = create_engine(
+         DATABASE_URL,
+         connect_args={"check_same_thread": False},
+         poolclass=StaticPool,
+     )
+ else:
+ ... (更多)
```

### backend/models.py (新建, 5948 chars)
```
+ from datetime import datetime
+ from flask_sqlalchemy import SQLAlchemy
+ from sqlalchemy import Index
+ 
+ db = SQLAlchemy()
+ 
+ 
+ class User(db.Model):
+     __tablename__ = 'users'
+     
+     id = db.Column(db.Integer, primary_key=True)
+     username = db.Column(db.String(80), unique=True, nullable=False)
+     email = db.Column(db.String(120), unique=True, nullable=False)
+     password_hash = db.Column(db.String(255), nullable=False)
+     created_at = db.Column(db.DateTime, default=datetime.utcnow)
+     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
+     
+     # Relationships
+     categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
+     transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
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
