from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    PasswordChange,
    UserPreferences,
    UserPreferencesUpdate
)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_info(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户信息
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
        current_user.email = user_update.email

    # 检查用户名是否已被其他用户使用
    if user_update.username and user_update.username != current_user.username:
        existing_user = db.query(User).filter(
            User.username == user_update.username,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被使用"
            )
        current_user.username = user_update.username

    # 更新其他字段
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    
    if user_update.avatar is not None:
        current_user.avatar = user_update.avatar
    
    if user_update.bio is not None:
        current_user.bio = user_update.bio

    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/me/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码
    """
    # 验证旧密码
    if not verify_password(password_change.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码不正确"
        )
    
    # 验证新密码和确认密码是否一致
    if password_change.new_password != password_change.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="两次输入的新密码不一致"
        )
    
    # 验证新密码长度
    if len(password_change.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度不能少于6位"
        )
    
    # 更新密码
    current_user.hashed_password = get_password_hash(password_change.new_password)
    db.commit()
    
    return {"message": "密码修改成功"}


@router.get("/me/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    获取用户偏好设置
    """
    preferences = {
        "theme": current_user.preferences.get("theme", "light") if current_user.preferences else "light",
        "language": current_user.preferences.get("language", "zh-CN") if current_user.preferences else "zh-CN",
        "notifications_enabled": current_user.preferences.get("notifications_enabled", True) if current_user.preferences else True,
        "email_notifications": current_user.preferences.get("email_notifications", True) if current_user.preferences else True,
        "show_online_status": current_user.preferences.get("show_online_status", True) if current_user.preferences else True,
        "timezone": current_user.preferences.get("timezone", "Asia/Shanghai") if current_user.preferences else "Asia/Shanghai",
    }
    return preferences


@router.put("/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences_update: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户偏好设置
    """
    # 获取当前偏好设置
    current_preferences = current_user.preferences or {}
    
    # 更新偏好设置
    update_data = preferences_update.dict(exclude_unset=True)
    current_preferences.update(update_data)
    
    current_user.preferences = current_preferences
    db.commit()
    db.refresh(current_user)
    
    return current_preferences


@router.delete("/me")
async def delete_user_account(
    password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除用户账户（需要验证密码）
    """
    # 验证密码
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码不正确"
        )
    
    # 软删除用户
    current_user.is_active = False
    db.commit()
    
    return {"message": "账户已删除"}


@router.post("/me/avatar")
async def upload_avatar(
    avatar_url: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传用户头像
    """
    current_user.avatar = avatar_url
    db.commit()
    db.refresh(current_user)
    
    return {"message": "头像上传成功", "avatar": avatar_url}


@router.get("/me/statistics")
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户统计信息
    """
    # 这里可以根据实际业务需求添加统计信息
    # 例如：发布的文章数、评论数、点赞数等
    statistics = {
        "user_id": current_user.id,
        "member_since": current_user.created_at,
        "last_login": current_user.last_login if hasattr(current_user, 'last_login') else None,
        "total_posts": 0,  # 需要根据实际业务实现
        "total_comments": 0,  # 需要根据实际业务实现
        "total_likes": 0,  # 需要根据实际业务实现
    }
    
    return statistics