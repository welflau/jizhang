from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from ..database import get_db
from ..models import User
from ..auth import get_current_user, get_password_hash, verify_password

router = APIRouter(
    prefix="/api/user",
    tags=["user"]
)


# Pydantic 模型
class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class UserPreferences(BaseModel):
    theme: Optional[str] = Field("light", pattern="^(light|dark|auto)$")
    language: Optional[str] = Field("zh-CN", pattern="^(zh-CN|en-US)$")
    notifications_enabled: Optional[bool] = True
    email_notifications: Optional[bool] = True


class UserPreferencesResponse(BaseModel):
    theme: str
    language: str
    notifications_enabled: bool
    email_notifications: bool


# 获取当前用户信息
@router.get("/profile", response_model=UserInfo)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户的个人信息
    """
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar=current_user.avatar,
        phone=current_user.phone,
        bio=current_user.bio,
        created_at=current_user.created_at.isoformat() if current_user.created_at else ""
    )


# 更新用户信息
@router.put("/profile", response_model=UserInfo)
async def update_user_profile(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户的个人信息
    """
    # 检查邮箱是否已被其他用户使用
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
    
    # 更新用户信息
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar=current_user.avatar,
        phone=current_user.phone,
        bio=current_user.bio,
        created_at=current_user.created_at.isoformat() if current_user.created_at else ""
    )


# 修改密码
@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改当前用户的密码
    """
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 检查新密码是否与旧密码相同
    if password_data.old_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与原密码相同"
        )
    
    # 更新密码
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "密码修改成功"}


# 获取用户偏好设置
@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的偏好设置
    """
    preferences = current_user.preferences or {}
    
    return UserPreferencesResponse(
        theme=preferences.get("theme", "light"),
        language=preferences.get("language", "zh-CN"),
        notifications_enabled=preferences.get("notifications_enabled", True),
        email_notifications=preferences.get("email_notifications", True)
    )


# 更新用户偏好设置
@router.put("/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户的偏好设置
    """
    # 获取现有偏好设置
    current_preferences = current_user.preferences or {}
    
    # 更新偏好设置
    update_data = preferences.model_dump(exclude_unset=True)
    current_preferences.update(update_data)
    
    current_user.preferences = current_preferences
    db.commit()
    db.refresh(current_user)
    
    return UserPreferencesResponse(
        theme=current_preferences.get("theme", "light"),
        language=current_preferences.get("language", "zh-CN"),
        notifications_enabled=current_preferences.get("notifications_enabled", True),
        email_notifications=current_preferences.get("email_notifications", True)
    )


# 上传头像
@router.post("/avatar")
async def upload_avatar(
    avatar_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户头像
    """
    current_user.avatar = avatar_url
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "头像更新成功",
        "avatar": current_user.avatar
    }


# 删除账户
@router.delete("/account")
async def delete_account(
    password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除当前用户账户（需要验证密码）
    """
    # 验证密码
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码错误"
        )
    
    # 删除用户
    db.delete(current_user)
    db.commit()
    
    return {"message": "账户已删除"}