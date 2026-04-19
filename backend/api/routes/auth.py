"""认证 API 路由"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    phone: str | None = None
    email: str | None = None
    password: str | None = None


class RegisterRequest(BaseModel):
    nickname: str
    phone: str | None = None
    email: str | None = None
    password: str


@router.post("/login")
async def login(request: LoginRequest):
    """用户登录"""
    # TODO: 实现 JWT 认证
    return {
        "message": "登录功能开发中",
        "token": "dev-token-123",
    }


@router.post("/register")
async def register(request: RegisterRequest):
    """用户注册"""
    # TODO: 实现注册逻辑
    return {
        "message": f"欢迎 {request.nickname}！注册功能开发中。",
        "token": "dev-token-123",
    }
