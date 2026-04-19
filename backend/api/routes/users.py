"""用户 API 路由"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
async def get_current_user():
    """获取当前用户信息"""
    # TODO: 从 JWT 获取用户
    return {
        "id": "00000000-0000-0000-0000-000000000001",
        "nickname": "测试用户",
        "subscription_tier": "free",
        "daily_message_count": 0,
        "daily_message_limit": 20,
    }
