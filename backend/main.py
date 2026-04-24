"""
Embera · 余温 — FastAPI 后端服务
提供角色管理、对话、记忆、会员等 API
"""

import os
import time
import json
import asyncio
from typing import List, Optional, AsyncGenerator
from datetime import datetime, date

import httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.prompt_builder import build_messages, PERSONAS
from database.engine import get_db, init_db, engine, Base
from models.user import User
from models.conversation import Conversation
from models.memory import Memory

app = FastAPI(title="Embera API", version="0.3.0")

# ═══════════════════════════════════════════
# CORS — 允许前端调用
# ═══════════════════════════════════════════
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════
# 配置 — API Keys & 模型
# ═══════════════════════════════════════════
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# 模型路由：按会员等级分配
TIER_MODELS = {
    "free":    os.getenv("TIER_FREE_MODEL",    "gpt-4o-mini"),
    "silver":  os.getenv("TIER_SILVER_MODEL",  "gpt-4o-mini"),
    "gold":    os.getenv("TIER_GOLD_MODEL",    "gpt-4o"),
}

LLM_API_BASE = os.getenv("LLM_API_BASE", "https://openrouter.ai/api/v1")
LLM_API_KEY = OPENROUTER_API_KEY or OPENAI_API_KEY or ANTHROPIC_API_KEY

# ═══════════════════════════════════════════
# 会员系统配置
# ═══════════════════════════════════════════
TIER_LIMITS = {
    "free":   {"daily": 20,  "label": "免费用户"},
    "silver": {"daily": 50,  "label": "普通会员"},
    "gold":   {"daily": 99999, "label": "高级会员"},
}


# ═══════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════

class ChatRequest(BaseModel):
    char_id: str
    message: str
    user_id: str = "default"
    mode: str = "companion"
    user_mood: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    delay_ms: int
    memory_captured: Optional[str] = None
    tier_info: Optional[dict] = None


# ═══════════════════════════════════════════
# 数据库工具函数
# ═══════════════════════════════════════════

def _today_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")


async def get_or_create_user_db(session: AsyncSession, user_id: str) -> User:
    """获取或创建用户"""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            id=user_id,
            nickname="用户",
            subscription_tier="free",
            daily_message_count=0,
            daily_message_limit=20,
            last_reset_date=datetime.utcnow(),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def check_tier_db(session: AsyncSession, user_id: str) -> dict:
    """检查用户会员状态"""
    user = await get_or_create_user_db(session, user_id)
    today = _today_str()
    last_reset = user.last_reset_date.strftime("%Y-%m-%d") if user.last_reset_date else ""
    if last_reset != today:
        user.daily_message_count = 0
        user.last_reset_date = datetime.utcnow()
        await session.commit()
    
    tier = user.subscription_tier or "free"
    limit = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    used = user.daily_message_count or 0
    remaining = max(0, limit["daily"] - used)
    return {
        "tier": tier,
        "tier_label": limit["label"],
        "daily_limit": limit["daily"],
        "daily_used": used,
        "remaining": remaining,
        "can_chat": remaining > 0,
    }


async def consume_message_db(session: AsyncSession, user_id: str):
    """消耗一条消息配额"""
    user = await get_or_create_user_db(session, user_id)
    user.daily_message_count = (user.daily_message_count or 0) + 1
    await session.commit()


async def get_history_db(session: AsyncSession, user_id: str, char_id: str, limit: int = 50) -> List[dict]:
    """获取历史对话"""
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Conversation.character_id == char_id)
        .order_by(desc(Conversation.created_at))
        .limit(limit)
    )
    rows = result.scalars().all()
    # 按时间正序排列
    rows = list(reversed(rows))
    return [
        {"sender": "user" if r.role == "user" else "ai", "text": r.content, "timestamp": r.created_at.timestamp()}
        for r in rows
    ]


async def add_history_db(session: AsyncSession, user_id: str, char_id: str, role: str, text: str, model_used: str = None):
    """保存对话记录"""
    conv = Conversation(
        user_id=user_id,
        character_id=char_id,
        role=role,
        content=text,
        model_used=model_used,
    )
    session.add(conv)
    await session.commit()


async def get_memories_db(session: AsyncSession, user_id: str, char_id: str, limit: int = 20) -> List[dict]:
    """获取记忆列表"""
    result = await session.execute(
        select(Memory)
        .where(Memory.user_id == user_id)
        .where(Memory.character_id == char_id)
        .order_by(desc(Memory.created_at))
        .limit(limit)
    )
    rows = result.scalars().all()
    rows = list(reversed(rows))
    return [
        {"type": r.memory_type, "content": r.content, "timestamp": r.created_at.timestamp()}
        for r in rows
    ]


async def add_memory_db(session: AsyncSession, user_id: str, char_id: str, memory_type: str, content: str):
    """保存记忆"""
    mem = Memory(
        user_id=user_id,
        character_id=char_id,
        memory_type=memory_type,
        content=content,
    )
    session.add(mem)
    await session.commit()


def extract_memory(text: str) -> Optional[str]:
    keywords = {
        "累": "用户最近很累",
        "烦": "用户最近很烦",
        "压力": "用户压力大",
        "难过": "用户情绪低落",
        "开心": "用户心情不错",
        "想": "用户有想念的人",
    }
    for kw, mem_type in keywords.items():
        if kw in text:
            return mem_type
    return None


# ═══════════════════════════════════════════
# LLM 调用（非流式 & 流式）
# ═══════════════════════════════════════════

async def call_llm(messages: List[dict], model: str = None) -> str:
    if not LLM_API_KEY:
        return "（后端未配置 LLM API Key，请设置环境变量 OPENROUTER_API_KEY 或 OPENAI_API_KEY）"

    model = model or TIER_MODELS.get("free")
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    if "openrouter" in LLM_API_BASE:
        headers["HTTP-Referer"] = "https://embera.app"
        headers["X-Title"] = "Embera"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 200,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{LLM_API_BASE}/chat/completions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def call_llm_stream(messages: List[dict], model: str = None) -> AsyncGenerator[str, None]:
    if not LLM_API_KEY:
        demo_replies = [
            "嗯...", "我在听。", "今天", "过得", "还好吗。",
            "累了的话...", "就", "先", "这样吧。",
        ]
        for word in demo_replies:
            yield "data: " + json.dumps({"type": "chunk", "content": word}) + "\n\n"
            await asyncio.sleep(0.3)
        yield "data: " + json.dumps({"type": "done"}) + "\n\n"
        return

    model = model or TIER_MODELS.get("free")
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    if "openrouter" in LLM_API_BASE:
        headers["HTTP-Referer"] = "https://embera.app"
        headers["X-Title"] = "Embera"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 200,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream(
            "POST",
            f"{LLM_API_BASE}/chat/completions",
            headers=headers,
            json=payload,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        yield "data: " + json.dumps({"type": "done"}) + "\n\n"
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta and delta["content"]:
                            yield "data: " + json.dumps({
                                "type": "chunk",
                                "content": delta["content"],
                            }) + "\n\n"
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue


# ═══════════════════════════════════════════
# 路由 — 健康检查
# ═══════════════════════════════════════════

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "0.3.0",
        "models": TIER_MODELS,
        "db": "sqlite",
    }


# ═══════════════════════════════════════════
# 路由 — 用户状态（会员信息）
# ═══════════════════════════════════════════

@app.get("/api/user/status")
async def user_status(user_id: str = "default", session: AsyncSession = Depends(get_db)):
    return await check_tier_db(session, user_id)


@app.post("/api/user/upgrade")
async def user_upgrade(user_id: str = "default", tier: str = "silver", session: AsyncSession = Depends(get_db)):
    if tier not in TIER_LIMITS:
        raise HTTPException(status_code=400, detail="无效的会员等级")
    user = await get_or_create_user_db(session, user_id)
    user.subscription_tier = tier
    await session.commit()
    return {"success": True, "tier": tier, "message": f"已升级为 {TIER_LIMITS[tier]['label']}"}


# ═══════════════════════════════════════════
# 路由 — 非流式对话
# ═══════════════════════════════════════════

@app.post("/api/chat/send", response_model=ChatResponse)
async def chat_send(req: ChatRequest, session: AsyncSession = Depends(get_db)):
    start = time.time()

    tier_info = await check_tier_db(session, req.user_id)
    if not tier_info["can_chat"]:
        return ChatResponse(
            reply="今天的对话次数用完了呢…明天再来吧。或者，升级会员可以无限对话。",
            delay_ms=0,
            memory_captured=None,
            tier_info=tier_info,
        )

    await consume_message_db(session, req.user_id)

    memories = await get_memories_db(session, req.user_id, req.char_id)
    history = await get_history_db(session, req.user_id, req.char_id)

    messages = build_messages(
        char_id=req.char_id,
        user_message=req.message,
        history=history,
        mode=req.mode,
        memories=memories,
        user_mood=req.user_mood,
    )

    user = await get_or_create_user_db(session, req.user_id)
    model = TIER_MODELS.get(user.subscription_tier or "free", TIER_MODELS["free"])

    reply = await call_llm(messages, model=model)
    print(f"[DEBUG] chat_send after LLM, user={req.user_id}")

    await add_history_db(session, req.user_id, req.char_id, "user", req.message, model)
    await add_history_db(session, req.user_id, req.char_id, "assistant", reply, model)
    print(f"[DEBUG] chat_send after history, user={req.user_id}")

    memory_captured = extract_memory(req.message)
    if memory_captured:
        await add_memory_db(session, req.user_id, req.char_id, memory_captured, req.message)

    base_delay = 1500 if req.mode == "memorial" else 800
    elapsed = int((time.time() - start) * 1000)
    delay_ms = max(base_delay, elapsed)

    tier_info = await check_tier_db(session, req.user_id)
    print(f"[DEBUG] chat_send final tier_info: {tier_info}")

    return ChatResponse(
        reply=reply,
        delay_ms=delay_ms,
        memory_captured=memory_captured,
        tier_info=tier_info,
    )


# ═══════════════════════════════════════════
# 路由 — 流式对话（SSE）
# ═══════════════════════════════════════════

@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest, session: AsyncSession = Depends(get_db)):
    async def event_generator() -> AsyncGenerator[str, None]:
        tier_info = await check_tier_db(session, req.user_id)
        if not tier_info["can_chat"]:
            yield "data: " + json.dumps({
                "type": "error",
                "content": "今天的对话次数用完了呢…明天再来吧。或者，升级会员可以无限对话。",
                "tier_info": tier_info,
            }) + "\n\n"
            yield "data: " + json.dumps({"type": "done"}) + "\n\n"
            return

        await consume_message_db(session, req.user_id)
        yield "data: " + json.dumps({"type": "tier_info", "tier_info": tier_info}) + "\n\n"

        memories = await get_memories_db(session, req.user_id, req.char_id)
        history = await get_history_db(session, req.user_id, req.char_id)

        messages = build_messages(
            char_id=req.char_id,
            user_message=req.message,
            history=history,
            mode=req.mode,
            memories=memories,
            user_mood=req.user_mood,
        )

        user = await get_or_create_user_db(session, req.user_id)
        model = TIER_MODELS.get(user.subscription_tier or "free", TIER_MODELS["free"])

        full_reply = ""
        async for event in call_llm_stream(messages, model=model):
            yield event
            try:
                data = json.loads(event.replace("data: ", "").strip())
                if data.get("type") == "chunk":
                    full_reply += data["content"]
            except:
                pass

        await add_history_db(session, req.user_id, req.char_id, "user", req.message, model)
        await add_history_db(session, req.user_id, req.char_id, "assistant", full_reply, model)

        memory_captured = extract_memory(req.message)
        if memory_captured:
            await add_memory_db(session, req.user_id, req.char_id, memory_captured, req.message)

        final_tier = await check_tier_db(session, req.user_id)
        yield "data: " + json.dumps({"type": "tier_info", "tier_info": final_tier}) + "\n\n"
        yield "data: " + json.dumps({"type": "done"}) + "\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ═══════════════════════════════════════════
# 路由 — 角色管理
# ═══════════════════════════════════════════

@app.get("/api/characters/list")
async def char_list():
    return [
        {
            "id": p["id"],
            "name": p["name"],
            "type": p["type"],
            "tagline": p["personality"],
            "avatar": p["id"],
        }
        for p in PERSONAS.values()
    ]


@app.get("/api/characters/templates")
async def char_templates():
    return {
        "templates": [
            {
                "id": p["id"],
                "name": p["name"],
                "type": p["type"],
                "personality": [p["personality"][:20] + "…"],
            }
            for p in PERSONAS.values()
        ]
    }


@app.get("/api/characters/{char_id}")
async def char_detail(char_id: str):
    if char_id not in PERSONAS:
        raise HTTPException(status_code=404, detail="角色不存在")
    p = PERSONAS[char_id]
    return {
        "id": p["id"],
        "name": p["name"],
        "type": p["type"],
        "personality": p["personality"],
        "first_meet": p.get("first_meet", ""),
    }


@app.post("/api/characters/create")
async def char_create(req: dict):
    persona_id = req.get("persona_id", "gf_gentle")
    if persona_id not in PERSONAS:
        raise HTTPException(status_code=404, detail="人设不存在")
    p = PERSONAS[persona_id]
    custom_name = req.get("custom_name") or p["name"]
    return {
        "id": persona_id,
        "name": custom_name,
        "type": p["type"],
        "avatar": persona_id,
    }


# ═══════════════════════════════════════════
# 路由 — 宠物（占位）
# ═══════════════════════════════════════════

@app.get("/api/pets/list")
async def pets_list():
    return {"pets": []}


@app.get("/api/pets/species")
async def pets_species():
    return {"species": ["cat", "dog", "rabbit", "panda", "fox", "dragon", "robot"]}


# ═══════════════════════════════════════════
# 路由 — 纪念（占位）
# ═══════════════════════════════════════════

@app.get("/api/memorial/list")
async def memorial_list():
    return {"memorials": []}


# ═══════════════════════════════════════════
# 启动
# ═══════════════════════════════════════════

@app.on_event("startup")
async def startup():
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
