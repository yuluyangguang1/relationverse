"""对话 API 路由"""

import os
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from database.engine import get_db
from models.user import User
from models.character import Character
from models.conversation import Conversation

router = APIRouter()


class ChatRequest(BaseModel):
    character_id: str
    message: str
    content_type: str = "text"  # text/voice


class ChatResponse(BaseModel):
    reply: str
    character_name: str
    intimacy_change: float
    relationship_stage: str
    tts_url: str | None = None


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """发送消息给角色"""
    # TODO: 实现完整的对话逻辑
    # 1. 获取角色信息
    # 2. 检索相关记忆
    # 3. 构建 prompt
    # 4. 调用 LLM 生成回复
    # 5. 保存对话记录
    # 6. 更新亲密度
    # 7. 可选：生成 TTS 语音
    
    # 临时响应（MVP 阶段）
    result = await db.execute(
        select(Character).where(Character.id == request.character_id)
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 保存用户消息
    user_msg = Conversation(
        user_id=character.owner_id,
        character_id=character.id,
        role="user",
        content=request.message,
        content_type=request.content_type,
    )
    db.add(user_msg)
    
    # 生成回复（临时）
    reply = f"收到你的消息：{request.message}。这是一个临时回复，LLM 对话功能正在开发中。"
    
    # 保存 AI 回复
    ai_msg = Conversation(
        user_id=character.owner_id,
        character_id=character.id,
        role="assistant",
        content=reply,
    )
    db.add(ai_msg)
    
    # 更新统计
    character.total_messages += 2
    character.last_active = datetime.utcnow()
    
    await db.commit()
    
    return ChatResponse(
        reply=reply,
        character_name=character.name,
        intimacy_change=0.5,
        relationship_stage=character.relationship_stage,
        tts_url=None,
    )


@router.get("/history/{character_id}")
async def get_history(
    character_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """获取对话历史"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.character_id == character_id)
        .order_by(Conversation.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    messages = result.scalars().all()
    
    return {
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "content_type": m.content_type,
                "created_at": m.created_at.isoformat(),
            }
            for m in reversed(messages)
        ]
    }
