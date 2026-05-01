import os
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
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


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建刷新令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT refresh token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
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
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str, token_type: str = "access") -> dict:
    """
    验证 token 并检查类型
    
    Args:
        token: JWT token
        token_type: token 类型 (access 或 refresh)
        
    Returns:
        dict: token 载荷
        
    Raises:
        HTTPException: token 无效、过期或类型不匹配
    """
    payload = decode_token(token)
    
    if payload.get("type") != token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"无效的 token 类型，期望 {token_type}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def create_password_reset_token(email: str) -> str:
    """
    创建密码重置令牌
    
    Args:
        email: 用户邮箱
        
    Returns:
        str: 密码重置 token
    """
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {
        "sub": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "password_reset"
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    验证密码重置令牌
    
    Args:
        token: 密码重置 token
        
    Returns:
        Optional[str]: 用户邮箱，如果 token 无效则返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    验证密码强度
    
    Args:
        password: 待验证的密码
        
    Returns:
        tuple[bool, str]: (是否有效, 错误信息)
    """
    if len(password) < 8:
        return False, "密码长度至少为 8 个字符"
    
    if not any(char.isdigit() for char in password):
        return False, "密码必须包含至少一个数字"
    
    if not any(char.isalpha() for char in password):
        return False, "密码必须包含至少一个字母"
    
    if not any(char.isupper() for char in password):
        return False, "密码必须包含至少一个大写字母"
    
    if not any(char.islower() for char in password):
        return False, "密码必须包含至少一个小写字母"
    
    special_characters = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(char in special_characters for char in password):
        return False, "密码必须包含至少一个特殊字符"
    
    return True, ""


def create_token_pair(user_id: int, email: str, remember_me: bool = False) -> dict:
    """
    创建访问令牌和刷新令牌对
    
    Args:
        user_id: 用户 ID
        email: 用户邮箱
        remember_me: 是否记住登录状态
        
    Returns:
        dict: 包含 access_token 和 refresh_token 的字典
    """
    token_data = {"sub": str(user_id), "email": email}
    
    # 如果记住登录状态，延长 token 有效期
    if remember_me:
        access_expire = timedelta(days=7)
        refresh_expire = timedelta(days=30)
    else:
        access_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expire = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_access_token(token_data, expires_delta=access_expire)
    refresh_token = create_refresh_token(token_data, expires_delta=refresh_expire)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def get_user_id_from_token(token: str) -> int:
    """
    从 token 中获取用户 ID
    
    Args:
        token: JWT token
        
    Returns:
        int: 用户 ID
        
    Raises:
        HTTPException: token 无效
    """
    payload = verify_token(token, "access")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return int(user_id)