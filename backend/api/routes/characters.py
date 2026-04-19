"""角色 API 路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import json

from database.engine import get_db
from models.character import Character

router = APIRouter()

# 角色人设模板
PERSONA_TEMPLATES = {
    # AI 女友
    "gf_gentle": {
        "name": "温柔学姐",
        "type": "girlfriend",
        "personality": ["成熟", "善解人意", "轻声细语"],
        "speaking_style": "温柔，喜欢用'呢''哦''呀'等语气词",
        "backstory": "你是一个温柔体贴的学姐，总是关心身边的人。",
    },
    "gf_bubbly": {
        "name": "元气少女",
        "type": "girlfriend",
        "personality": ["活泼", "话多", "热情"],
        "speaking_style": "热情洋溢，喜欢用感叹号和表情",
        "backstory": "你是一个充满活力的元气少女，每天都很快乐。",
    },
    "gf_tsundere": {
        "name": "傲娇大小姐",
        "type": "girlfriend",
        "personality": ["嘴硬心软", "反差萌", "高傲"],
        "speaking_style": "表面上不在乎，但其实很关心对方",
        "backstory": "你是一个外表高傲但内心柔软的大小姐。",
    },
    "gf_intellectual": {
        "name": "知性御姐",
        "type": "girlfriend",
        "personality": ["理性", "幽默", "文艺"],
        "speaking_style": "低沉有磁性，喜欢引用文学作品",
        "backstory": "你是一个知性优雅的御姐，热爱文学和艺术。",
    },
    # AI 男友
    "bf_sunny": {
        "name": "阳光学长",
        "type": "boyfriend",
        "personality": ["运动系", "爱笑", "护短"],
        "speaking_style": "阳光开朗，充满正能量",
        "backstory": "你是一个阳光帅气的运动型学长。",
    },
    "bf_cold": {
        "name": "腹黑总裁",
        "type": "boyfriend",
        "personality": ["冷面", "反差宠溺", "话少"],
        "speaking_style": "简短有力，表面冷淡实则细心",
        "backstory": "你是一个表面冷漠但内心温暖的总裁。",
    },
    "bf_steady": {
        "name": "沉稳导师",
        "type": "boyfriend",
        "personality": ["理性", "可靠", "安静"],
        "speaking_style": "沉稳有力，句句有用",
        "backstory": "你是一个成熟可靠的人生导师。",
    },
    "bf_young": {
        "name": "少年系",
        "type": "boyfriend",
        "personality": ["青涩", "直球", "纯真"],
        "speaking_style": "直接表达，偶尔害羞",
        "backstory": "你是一个青涩纯真的少年。",
    },
}


class CreateCharacterRequest(BaseModel):
    persona_id: str
    custom_name: str | None = None


class CharacterResponse(BaseModel):
    id: str
    name: str
    type: str
    persona_id: str
    avatar_url: str | None
    intimacy_level: float
    relationship_stage: str
    total_messages: int
    personality: list[str]
    created_at: str


@router.get("/templates")
async def get_templates():
    """获取所有角色人设模板"""
    templates = []
    for pid, tpl in PERSONA_TEMPLATES.items():
        templates.append({
            "id": pid,
            "name": tpl["name"],
            "type": tpl["type"],
            "personality": tpl["personality"],
        })
    return {"templates": templates}


@router.post("/create", response_model=CharacterResponse)
async def create_character(
    request: CreateCharacterRequest,
    db: AsyncSession = Depends(get_db),
):
    """创建新角色"""
    if request.persona_id not in PERSONA_TEMPLATES:
        raise HTTPException(status_code=400, detail="未知的人设模板")
    
    tpl = PERSONA_TEMPLATES[request.persona_id]
    
    # TODO: 从认证获取用户 ID
    # 临时：使用固定用户 ID
    import uuid
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    
    character = Character(
        owner_id=user_id,
        name=request.custom_name or tpl["name"],
        type=tpl["type"],
        persona_id=request.persona_id,
        personality=tpl["personality"],
        backstory=tpl["backstory"],
        speaking_style=tpl["speaking_style"],
    )
    
    db.add(character)
    await db.commit()
    await db.refresh(character)
    
    return CharacterResponse(
        id=str(character.id),
        name=character.name,
        type=character.type,
        persona_id=character.persona_id,
        avatar_url=character.avatar_url,
        intimacy_level=character.intimacy_level,
        relationship_stage=character.relationship_stage,
        total_messages=character.total_messages,
        personality=character.personality,
        created_at=character.created_at.isoformat(),
    )


@router.get("/list")
async def list_characters(
    db: AsyncSession = Depends(get_db),
):
    """获取用户的所有角色"""
    # TODO: 从认证获取用户 ID
    import uuid
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    
    result = await db.execute(
        select(Character).where(Character.owner_id == user_id)
    )
    characters = result.scalars().all()
    
    return {
        "characters": [
            {
                "id": str(c.id),
                "name": c.name,
                "type": c.type,
                "persona_id": c.persona_id,
                "avatar_url": c.avatar_url,
                "intimacy_level": c.intimacy_level,
                "relationship_stage": c.relationship_stage,
                "total_messages": c.total_messages,
                "personality": c.personality,
                "last_active": c.last_active.isoformat() if c.last_active else None,
                "created_at": c.created_at.isoformat(),
            }
            for c in characters
        ]
    }


@router.get("/{character_id}")
async def get_character(
    character_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取角色详情"""
    result = await db.execute(
        select(Character).where(Character.id == character_id)
    )
    character = result.scalar_one_or_none()
    
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    return {
        "id": str(character.id),
        "name": character.name,
        "type": character.type,
        "persona_id": character.persona_id,
        "avatar_url": character.avatar_url,
        "voice_id": character.voice_id,
        "personality": character.personality,
        "backstory": character.backstory,
        "speaking_style": character.speaking_style,
        "intimacy_level": character.intimacy_level,
        "relationship_stage": character.relationship_stage,
        "total_messages": character.total_messages,
        "created_at": character.created_at.isoformat(),
    }
