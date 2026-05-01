from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import re

from backend.database import get_db
from backend.models import User, PasswordResetToken
from backend.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    PasswordResetRequest,
    PasswordReset,
    MessageResponse
)
from backend.config import settings
from backend.utils.email import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 密码验证正则
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_REGEX = re.compile(r"^1[3-9]\d{9}$")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """密码加密"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    
    return user


def validate_password(password: str) -> None:
    """验证密码强度"""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少为8位"
        )
    if not PASSWORD_REGEX.match(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码必须包含字母和数字"
        )


def validate_email_or_phone(identifier: str) -> tuple[str, str]:
    """验证并识别邮箱或手机号"""
    if EMAIL_REGEX.match(identifier):
        return "email", identifier
    elif PHONE_REGEX.match(identifier):
        return "phone", identifier
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入有效的邮箱或手机号"
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 验证密码强度
    validate_password(user_data.password)
    
    # 识别注册方式（邮箱或手机号）
    identifier_type, identifier_value = validate_email_or_phone(user_data.email_or_phone)
    
    # 检查用户是否已存在
    existing_user = None
    if identifier_type == "email":
        existing_user = db.query(User).filter(User.email == identifier_value).first()
    else:
        existing_user = db.query(User).filter(User.phone == identifier_value).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该{'邮箱' if identifier_type == 'email' else '手机号'}已被注册"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=identifier_value if identifier_type == "email" else None,
        phone=identifier_value if identifier_type == "phone" else None,
        username=user_data.username or identifier_value,
        hashed_password=hashed_password,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    remember_me: bool = False,
    db: Session = Depends(get_db)
):
    """用户登录"""
    # 识别登录方式
    identifier_type, identifier_value = validate_email_or_phone(form_data.username)
    
    # 查找用户
    user = None
    if identifier_type == "email":
        user = db.query(User).filter(User.email == identifier_value).first()
    else:
        user = db.query(User).filter(User.phone == identifier_value).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()
    
    # 创建访问令牌
    access_token_expires = timedelta(
        days=30 if remember_me else minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    # 创建刷新令牌
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds())
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """刷新访问令牌"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的刷新令牌",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise credentials_exception
    
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds())
    }


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出"""
    # 在实际应用中，可以将令牌加入黑名单
    # 这里简单返回成功消息
    return {"message": "登出成功"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.post("/password-reset-request", response_model=MessageResponse)
async def request_password_reset(
    request_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """请求密码重置"""
    # 识别邮箱或手机号
    identifier_type, identifier_value = validate_email_or_phone(request_data.email_or_phone)
    
    # 查找用户
    user = None
    if identifier_type == "email":
        user = db.query(User).filter(User.email == identifier_value).first()
    else:
        user = db.query(User).filter(User.phone == identifier_value).first()
    
    # 即使用户不存在也返回成功，防止用户枚举
    if not user:
        return {"message": "如果该账号存在，重置链接已发送"}
    
    # 生成重置令牌
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    # 删除旧的重置令牌
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id
    ).delete()
    
    # 保存新令牌
    password_reset_token = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at
    )
    db.add(password_reset_token)
    db.commit()
    
    # 发送重置邮件（后台任务）
    if identifier_type == "email":
        background_tasks.add_task(
            send_password_reset_email,
            email=user.email,
            token=reset_token,
            username=user.username
        )
    
    return {"message": "如果该账号存在，重置链接已发送"}


@router.post("/password-reset", response_model=MessageResponse)
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """重置密码"""
    # 验证新密码强度
    validate_password(reset_data.new_password)
    
    # 查找重置令牌
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == reset_data.token
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的重置令牌"
        )
    
    # 检查令牌是否过期
    if reset_token.expires_at < datetime.utcnow():
        db.delete(reset_token)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置令牌已过期"
        )
    
    # 更新用户密码
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user.hashed_password = get_password_hash(reset_data.new_password)
    
    # 删除重置令牌
    db.delete(reset_token)
    db.commit()
    
    return {"message": "密码重置成功"}


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证旧密码
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 验证新密码强度
    validate_password(new_password)
    
    # 更新密码
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "密码修改成功"}