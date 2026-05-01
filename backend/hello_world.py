from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import bcrypt
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import re

load_dotenv()

app = FastAPI(title="User Authentication System")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

security = HTTPBearer()

# 模拟数据库（生产环境请使用真实数据库）
users_db = {}
reset_tokens_db = {}


# 数据模型
class UserRegister(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str = Field(..., min_length=6)
    username: str = Field(..., min_length=3)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "phone": "13800138000",
                "password": "password123",
                "username": "johndoe"
            }
        }


class UserLogin(BaseModel):
    identifier: str  # 邮箱或手机号
    password: str
    remember_me: bool = False


class PasswordReset(BaseModel):
    identifier: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None


# 工具函数
def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def hash_password(password: str) -> str:
    """密码加密"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_token(data: dict, expires_delta: timedelta) -> str:
    """创建JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """解码JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token已过期"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token"
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """获取当前用户"""
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("sub")
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    return users_db[user_id]


# API路由
@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """用户注册"""
    if not user_data.email and not user_data.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱或手机号至少提供一个"
        )
    
    if user_data.phone and not validate_phone(user_data.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 检查用户是否已存在
    for user in users_db.values():
        if user_data.email and user.get("email") == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        if user_data.phone and user.get("phone") == user_data.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )
        if user.get("username") == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被使用"
            )
    
    # 创建新用户
    user_id = f"user_{len(users_db) + 1}"
    hashed_pwd = hash_password(user_data.password)
    
    new_user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "phone": user_data.phone,
        "password": hashed_pwd,
        "created_at": datetime.utcnow().isoformat()
    }
    
    users_db[user_id] = new_user
    
    return UserResponse(
        id=user_id,
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone
    )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    """用户登录"""
    user = None
    
    # 查找用户
    for u in users_db.values():
        if u.get("email") == login_data.identifier or u.get("phone") == login_data.identifier:
            user = u
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": user["id"], "type": "access"},
        expires_delta=access_token_expires
    )
    
    refresh_token = None
    if login_data.remember_me:
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_token(
            data={"sub": user["id"], "type": "refresh"},
            expires_delta=refresh_token_expires
        )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@app.post("/api/auth/refresh", response_model=TokenResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """刷新token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的refresh token"
        )
    
    user_id = payload.get("sub")
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    
    # 创建新的access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": user_id, "type": "access"},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(access_token=access_token)


@app.post("/api/auth/password-reset")
async def request_password_reset(reset_data: PasswordReset):
    """请求密码重置"""
    user = None
    
    # 查找用户
    for u in users_db.values():
        if u.get("email") == reset_data.identifier or u.get("phone") == reset_data.identifier:
            user = u
            break
    
    if not user:
        # 为了安全，不透露用户是否存在
        return {"message": "如果该账户存在，重置链接已发送"}
    
    # 创建重置token（有效期15分钟）
    reset_token = create_token(
        data={"sub": user["id"], "type": "reset"},
        expires_delta=timedelta(minutes=15)
    )
    
    reset_tokens_db[reset_token] = user["id"]
    
    # 实际应用中应该发送邮件或短信
    print(f"密码重置token: {reset_token}")
    
    return {"message": "如果该账户存在，重置链接已发送"}


@app.post("/api/auth/password-reset/confirm")
async def confirm_password_reset(reset_confirm: PasswordResetConfirm):
    """确认密码重置"""
    if reset_confirm.token not in reset_tokens_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效或已过期的重置token"
        )
    
    payload = decode_token(reset_confirm.token)
    
    if payload.get("type") != "reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的重置token"
        )
    
    user_id = payload.get("sub")
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户不存在"
        )
    
    # 更新密码
    users_db[user_id]["password"] = hash_password(reset_confirm.new_password)
    
    # 删除已使用的token
    del reset_tokens_db[reset_confirm.token]
    
    return {"message": "密码重置成功"}


@app.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """用户登出"""
    # 在实际应用中，应该将token加入黑名单
    return {"message": "登出成功"}


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user.get("email"),
        phone=current_user.get("phone")
    )


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "User Authentication System API",
        "version": "1.0.0",
        "endpoints": {
            "register": "/api/auth/register",
            "login": "/api/auth/login",
            "refresh": "/api/auth/refresh",
            "password_reset": "/api/auth/password-reset",
            "password_reset_confirm": "/api/auth/password-reset/confirm",
            "logout": "/api/auth/logout",
            "me": "/api/auth/me"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)