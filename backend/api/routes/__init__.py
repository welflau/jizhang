from fastapi import APIRouter
from .auth import router as auth_router

api_router = APIRouter()

# 注册认证相关路由
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# 可以在这里继续添加其他路由模块
# api_router.include_router(user_router, prefix="/users", tags=["users"])
# api_router.include_router(profile_router, prefix="/profile", tags=["profile"])