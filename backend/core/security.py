from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import secrets
import os

from backend.core.config import settings
from backend.db.session import get_db
from backend.models.user import User

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "30"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    创建刷新令牌
    
    Args:
        data: 要编码的数据
        
    Returns:
        str: JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_reset_token(data: dict) -> str:
    """
    创建密码重置令牌
    
    Args:
        data: 要编码的数据
        
    Returns:
        str: JWT reset token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "reset"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    解码 JWT token
    
    Args:
        token: JWT token
        
    Returns:
        dict: 解码后的数据
        
    Raises:
        HTTPException: token 无效或过期
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token_type(payload: dict, expected_type: str) -> bool:
    """
    验证 token 类型
    
    Args:
        payload: token 载荷
        expected_type: 期望的类型
        
    Returns:
        bool: 类型是否匹配
    """
    token_type = payload.get("type")
    return token_type == expected_type


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    认证用户
    
    Args:
        db: 数据库会话
        username: 用户名（邮箱或手机号）
        password: 密码
        
    Returns:
        User: 用户对象，认证失败返回 None
    """
    # 尝试通过邮箱查找
    user = db.query(User).filter(User.email == username).first()
    
    # 如果邮箱未找到，尝试通过手机号查找
    if not user:
        user = db.query(User).filter(User.phone == username).first()
    
    # 验证密码
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    # 检查用户是否被禁用
    if not user.is_active:
        return None
    
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前用户
    
    Args:
        token: JWT token
        db: 数据库会话
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 认证失败
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
        
        # 验证 token 类型
        if not verify_token_type(payload, "access"):
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 活跃用户对象
        
    Raises:
        HTTPException: 用户未激活
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前超级用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 超级用户对象
        
    Raises:
        HTTPException: 权限不足
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    return current_user


def verify_reset_token(token: str) -> Optional[str]:
    """
    验证密码重置令牌
    
    Args:
        token: 重置令牌
        
    Returns:
        str: 用户ID，验证失败返回 None
    """
    try:
        payload = decode_token(token)
        
        # 验证 token 类型
        if not verify_token_type(payload, "reset"):
            return None
        
        user_id: str = payload.get("sub")
        return user_id
    except JWTError:
        return None


def generate_verification_code() -> str:
    """
    生成验证码（6位数字）
    
    Returns:
        str: 验证码
    """
    return str(secrets.randbelow(1000000)).zfill(6)


def generate_random_token(length: int = 32) -> str:
    """
    生成随机令牌
    
    Args:
        length: 令牌长度
        
    Returns:
        str: 随机令牌
    """
    return secrets.token_urlsafe(length)


class RateLimiter:
    """
    简单的速率限制器（基于内存）
    生产环境建议使用 Redis
    """
    
    def __init__(self):
        self.attempts = {}
    
    def check_rate_limit(
        self,
        key: str,
        max_attempts: int = 5,
        window_seconds: int = 300
    ) -> bool:
        """
        检查速率限制
        
        Args:
            key: 限制键（如 IP 地址或用户ID）
            max_attempts: 最大尝试次数
            window_seconds: 时间窗口（秒）
            
        Returns:
            bool: 是否允许请求
        """
        now = datetime.utcnow()
        
        if key not in self.attempts:
            self.attempts[key] = []
        
        # 清理过期记录
        self.attempts[key] = [
            attempt for attempt in self.attempts[key]
            if (now - attempt).total_seconds() < window_seconds
        ]
        
        # 检查是否超过限制
        if len(self.attempts[key]) >= max_attempts:
            return False
        
        # 记录本次尝试
        self.attempts[key].append(now)
        return True
    
    def reset(self, key: str):
        """
        重置速率限制
        
        Args:
            key: 限制键
        """
        if key in self.attempts:
            del self.attempts[key]


# 全局速率限制器实例
rate_limiter = RateLimiter()