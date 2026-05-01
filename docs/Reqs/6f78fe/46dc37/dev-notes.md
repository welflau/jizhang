# 开发笔记 — 个人中心页面 UI 实现

> 2026-05-02 01:42 | LLM

## 产出文件
- [backend/app/models/user.py](/app#repo?file=backend/app/models/user.py) (4333 chars)
- [backend/app/models/user_preference.py](/app#repo?file=backend/app/models/user_preference.py) (2947 chars)
- [backend/app/schemas/user.py](/app#repo?file=backend/app/schemas/user.py) (4083 chars)
- [backend/app/schemas/user_preference.py](/app#repo?file=backend/app/schemas/user_preference.py) (1925 chars)
- [backend/app/api/routes/user.py](/app#repo?file=backend/app/api/routes/user.py) (6205 chars)
- [backend/app/services/user_service.py](/app#repo?file=backend/app/services/user_service.py) (7897 chars)
- [backend/app/services/auth_service.py](/app#repo?file=backend/app/services/auth_service.py) (7408 chars)
- [backend/alembic/versions/004_create_users_table.py](/app#repo?file=backend/alembic/versions/004_create_users_table.py) (7741 chars)
- [backend/alembic/versions/005_create_user_preferences_table.py](/app#repo?file=backend/alembic/versions/005_create_user_preferences_table.py) (2948 chars)
- [frontend/src/pages/Profile.tsx](/app#repo?file=frontend/src/pages/Profile.tsx) (19235 chars)
- [frontend/src/components/profile/UserInfoCard.tsx](/app#repo?file=frontend/src/components/profile/UserInfoCard.tsx) (10032 chars)
- [frontend/src/components/profile/EditProfileForm.tsx](/app#repo?file=frontend/src/components/profile/EditProfileForm.tsx) (7705 chars)
- [frontend/src/components/profile/ChangePasswordModal.tsx](/app#repo?file=frontend/src/components/profile/ChangePasswordModal.tsx) (3999 chars)
- [frontend/src/components/profile/PreferencesPanel.tsx](/app#repo?file=frontend/src/components/profile/PreferencesPanel.tsx) (5653 chars)
- [frontend/src/api/user.ts](/app#repo?file=frontend/src/api/user.ts) (2180 chars)
- [frontend/src/types/user.ts](/app#repo?file=frontend/src/types/user.ts) (1998 chars)
- [backend/requirements.txt](/app#repo?file=backend/requirements.txt) (245 chars)
- [backend/app/main.py](/app#repo?file=backend/app/main.py) (1312 chars)

## 自测: 自测 5/6 通过 ⚠️

| 检查项 | 结果 | 说明 |
|--------|------|------|
| 文件产出 | ✅ | 18 个文件 |
| 入口文件 | ❌ | 缺少 |
| 代码非空 | ✅ | 通过 |
| 语法检查 | ✅ | 通过 |
| 文件名规范 | ✅ | 全英文 |
| 磁盘落地 | ✅ | 18 个文件已落盘 |

## 代码变更 (Diff)

### backend/app/models/user.py (新建, 4333 chars)
```
+ from datetime import datetime
+ from typing import Optional
+ from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
+ from sqlalchemy.orm import relationship
+ from werkzeug.security import generate_password_hash, check_password_hash
+ from app.database import Base
+ 
+ 
+ class User(Base):
+     """用户模型"""
+     __tablename__ = "users"
+ 
+     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
+     username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
+     email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
+     password_hash = Column(String(255), nullable=False, comment="密码哈希")
+     nickname = Column(String(50), nullable=True, comment="昵称")
+     avatar = Column(String(255), nullable=True, comment="头像URL")
+     phone = Column(String(20), nullable=True, comment="手机号")
+     bio = Column(Text, nullable=True, comment="个人简介")
+ ... (更多)
```

### backend/app/models/user_preference.py (新建, 2947 chars)
```
+ from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
+ from sqlalchemy.orm import relationship
+ from datetime import datetime
+ from app.database import Base
+ 
+ 
+ class UserPreference(Base):
+     """用户偏好设置模型"""
+     __tablename__ = "user_preferences"
+ 
+     id = Column(Integer, primary_key=True, index=True)
+     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
+     
+     # 通知设置
+     email_notifications = Column(Boolean, default=True, comment="邮件通知")
+     system_notifications = Column(Boolean, default=True, comment="系统通知")
+     task_reminders = Column(Boolean, default=True, comment="任务提醒")
+     
+     # 显示设置
+     theme = Column(String(20), default="light", comment="主题: light/dark/auto")
+ ... (更多)
```

### backend/app/schemas/user.py (新建, 4083 chars)
```
+ from pydantic import BaseModel, EmailStr, Field, validator
+ from typing import Optional
+ from datetime import datetime
+ 
+ 
+ class UserBase(BaseModel):
+     """用户基础模型"""
+     username: str = Field(..., min_length=3, max_length=50, description="用户名")
+     email: EmailStr = Field(..., description="邮箱")
+     full_name: Optional[str] = Field(None, max_length=100, description="全名")
+     phone: Optional[str] = Field(None, max_length=20, description="手机号")
+     avatar: Optional[str] = Field(None, description="头像URL")
+     bio: Optional[str] = Field(None, max_length=500, description="个人简介")
+ 
+ 
+ class UserCreate(UserBase):
+     """用户创建模型"""
+     password: str = Field(..., min_length=6, max_length=100, description="密码")
+ 
+     @validator('password')
+ ... (更多)
```

### backend/app/schemas/user_preference.py (新建, 1925 chars)
```
+ from pydantic import BaseModel, Field
+ from typing import Optional
+ from datetime import datetime
+ 
+ 
+ class UserPreferenceBase(BaseModel):
+     """用户偏好设置基础模型"""
+     theme: Optional[str] = Field(default="light", description="主题设置: light/dark/auto")
+     language: Optional[str] = Field(default="zh-CN", description="语言设置")
+     notification_enabled: Optional[bool] = Field(default=True, description="是否启用通知")
+     email_notification: Optional[bool] = Field(default=True, description="是否启用邮件通知")
+     timezone: Optional[str] = Field(default="Asia/Shanghai", description="时区设置")
+     date_format: Optional[str] = Field(default="YYYY-MM-DD", description="日期格式")
+     time_format: Optional[str] = Field(default="24h", description="时间格式: 12h/24h")
+     page_size: Optional[int] = Field(default=20, ge=10, le=100, description="每页显示数量")
+     auto_save: Optional[bool] = Field(default=True, description="是否自动保存")
+     show_tutorial: Optional[bool] = Field(default=True, description="是否显示新手引导")
+ 
+ 
+ class UserPreferenceCreate(UserPreferenceBase):
+ ... (更多)
```

### backend/app/api/routes/user.py (新建, 6205 chars)
```
+ from fastapi import APIRouter, Depends, HTTPException, status
+ from sqlalchemy.orm import Session
+ from typing import Optional
+ 
+ from app.core.database import get_db
+ from app.core.security import get_current_user, get_password_hash, verify_password
+ from app.models.user import User
+ from app.schemas.user import (
+     UserResponse,
+     UserUpdate,
+     PasswordChange,
+     UserPreferences,
+     UserPreferencesUpdate
+ )
+ 
+ router = APIRouter()
+ 
+ 
+ @router.get("/me", response_model=UserResponse)
+ async def get_current_user_info(
+ ... (更多)
```

### backend/app/services/user_service.py (新建, 7897 chars)
```
+ from typing import Optional, Dict, Any
+ from datetime import datetime
+ from sqlalchemy.orm import Session
+ from sqlalchemy.exc import IntegrityError
+ from app.models.user import User
+ from app.core.security import get_password_hash, verify_password
+ from app.schemas.user import UserCreate, UserUpdate, UserPreferences
+ 
+ 
+ class UserService:
+     """用户服务类，处理用户相关的业务逻辑"""
+ 
+     @staticmethod
+     def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
+         """根据用户ID获取用户信息"""
+         return db.query(User).filter(User.id == user_id).first()
+ 
+     @staticmethod
+     def get_user_by_email(db: Session, email: str) -> Optional[User]:
+         """根据邮箱获取用户信息"""
+ ... (更多)
```

### backend/app/services/auth_service.py (新建, 7408 chars)
```
+ import jwt
+ from datetime import datetime, timedelta
+ from typing import Optional, Dict, Any
+ from passlib.context import CryptContext
+ from sqlalchemy.orm import Session
+ from fastapi import HTTPException, status
+ 
+ from app.core.config import settings
+ from app.models.user import User
+ from app.schemas.user import UserCreate, UserUpdate, PasswordChange
+ 
+ pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
+ 
+ 
+ class AuthService:
+     """认证服务类"""
+ 
+     @staticmethod
+     def verify_password(plain_password: str, hashed_password: str) -> bool:
+         """验证密码"""
+ ... (更多)
```

### backend/alembic/versions/004_create_users_table.py (新建, 7741 chars)
```
+ """create users table
+ 
+ Revision ID: 004
+ Revises: 003
+ Create Date: 2024-01-01 00:00:00.000000
+ 
+ """
+ from alembic import op
+ import sqlalchemy as sa
+ from sqlalchemy.dialects import postgresql
+ 
+ # revision identifiers, used by Alembic.
+ revision = '004'
+ down_revision = '003'
+ branch_labels = None
+ depends_on = None
+ 
+ 
+ def upgrade() -> None:
+     # 创建用户表
+ ... (更多)
```

### backend/alembic/versions/005_create_user_preferences_table.py (新建, 2948 chars)
```
+ """create user preferences table
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
+     # 创建用户偏好设置表
+ ... (更多)
```

### frontend/src/pages/Profile.tsx (新建, 19235 chars)
```
+ import React, { useState, useEffect } from 'react';
+ import {
+   Box,
+   Container,
+   Paper,
+   Typography,
+   Avatar,
+   Button,
+   TextField,
+   Grid,
+   Divider,
+   Dialog,
+   DialogTitle,
+   DialogContent,
+   DialogActions,
+   Switch,
+   FormControlLabel,
+   Alert,
+   Snackbar,
+   IconButton,
+ ... (更多)
```

### frontend/src/components/profile/UserInfoCard.tsx (新建, 10032 chars)
```
+ import React, { useState } from 'react';
+ import { Card, Avatar, Button, Descriptions, Tag, Space, Modal, Form, Input, message, Upload } from 'antd';
+ import { EditOutlined, LockOutlined, UserOutlined, MailOutlined, PhoneOutlined, CameraOutlined } from '@ant-design/icons';
+ import type { UploadFile } from 'antd/es/upload/interface';
+ 
+ interface UserInfo {
+   id: string;
+   username: string;
+   email: string;
+   phone?: string;
+   avatar?: string;
+   nickname?: string;
+   role: string;
+   status: 'active' | 'inactive';
+   createdAt: string;
+   lastLoginAt?: string;
+ }
+ 
+ interface UserInfoCardProps {
+   userInfo: UserInfo;
+ ... (更多)
```

### frontend/src/components/profile/EditProfileForm.tsx (新建, 7705 chars)
```
+ import React, { useState, useEffect } from 'react';
+ import { Form, Input, Button, message, Upload, Avatar, Select, DatePicker } from 'antd';
+ import { UserOutlined, MailOutlined, PhoneOutlined, UploadOutlined, CameraOutlined } from '@ant-design/icons';
+ import type { UploadFile, UploadProps } from 'antd';
+ import dayjs from 'dayjs';
+ import { userAPI } from '../../services/api';
+ import './EditProfileForm.less';
+ 
+ const { Option } = Select;
+ 
+ interface UserProfile {
+   id: string;
+   username: string;
+   email: string;
+   phone?: string;
+   avatar?: string;
+   nickname?: string;
+   gender?: 'male' | 'female' | 'other';
+   birthday?: string;
+   bio?: string;
+ ... (更多)
```

### frontend/src/components/profile/ChangePasswordModal.tsx (新建, 3999 chars)
```
+ import React, { useState } from 'react';
+ import { Modal, Form, Input, Button, message } from 'antd';
+ import { LockOutlined } from '@ant-design/icons';
+ import { changePassword } from '../../services/user';
+ 
+ interface ChangePasswordModalProps {
+   visible: boolean;
+   onCancel: () => void;
+   onSuccess: () => void;
+ }
+ 
+ const ChangePasswordModal: React.FC<ChangePasswordModalProps> = ({
+   visible,
+   onCancel,
+   onSuccess,
+ }) => {
+   const [form] = Form.useForm();
+   const [loading, setLoading] = useState(false);
+ 
+   const handleSubmit = async (values: {
+ ... (更多)
```

### frontend/src/components/profile/PreferencesPanel.tsx (新建, 5653 chars)
```
+ import React, { useState, useEffect } from 'react';
+ import { Form, Switch, Select, Button, message, Card, Divider, Space } from 'antd';
+ import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';
+ import { userAPI } from '../../services/api';
+ 
+ const { Option } = Select;
+ 
+ interface PreferencesData {
+   language: string;
+   theme: string;
+   emailNotifications: boolean;
+   smsNotifications: boolean;
+   pushNotifications: boolean;
+   autoSave: boolean;
+   defaultView: string;
+   itemsPerPage: number;
+ }
+ 
+ const PreferencesPanel: React.FC = () => {
+   const [form] = Form.useForm();
+ ... (更多)
```

### frontend/src/api/user.ts (新建, 2180 chars)
```
+ import request from '@/utils/request';
+ 
+ export interface UserInfo {
+   id: number;
+   username: string;
+   email: string;
+   avatar?: string;
+   nickname?: string;
+   phone?: string;
+   gender?: number;
+   birthday?: string;
+   bio?: string;
+   createdAt: string;
+   updatedAt: string;
+ }
+ 
+ export interface UpdateUserInfoParams {
+   nickname?: string;
+   email?: string;
+   phone?: string;
+ ... (更多)
```

### frontend/src/types/user.ts (新建, 1998 chars)
```
+ export interface User {
+   id: string;
+   username: string;
+   email: string;
+   avatar?: string;
+   nickname?: string;
+   phone?: string;
+   bio?: string;
+   gender?: 'male' | 'female' | 'other';
+   birthday?: string;
+   location?: string;
+   website?: string;
+   createdAt: string;
+   updatedAt: string;
+ }
+ 
+ export interface UserProfile extends User {
+   followersCount?: number;
+   followingCount?: number;
+   postsCount?: number;
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

+from backend.app.routers import auth, user

 import logging

 

 # Configure logging

@@ -28,6 +28,7 @@
 

 # Include routers

 app.include_router(auth.router)

+app.include_router(user.router)

 

 

 @app.on_event("startup")

```
