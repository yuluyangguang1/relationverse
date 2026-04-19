"""数字怀念 API 路由"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from database.engine import get_db
from models.memorial import MemorialCharacter

router = APIRouter()


class CreateMemorialRequest(BaseModel):
    name: str
    relation_type: str  # parent/grandparent/sibling/friend/pet/other
    personality_desc: str | None = None
    catchphrases: list[str] = []


@router.post("/create")
async def create_memorial(
    request: CreateMemorialRequest,
    db: AsyncSession = Depends(get_db),
):
    """创建数字怀念角色"""
    import uuid
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    
    memorial = MemorialCharacter(
        owner_id=user_id,
        name=request.name,
        relation_type=request.relation_type,
        personality_desc=request.personality_desc,
        catchphrases=request.catchphrases,
    )
    
    db.add(memorial)
    await db.commit()
    await db.refresh(memorial)
    
    return {
        "id": str(memorial.id),
        "name": memorial.name,
        "relation_type": memorial.relation_type,
        "status": "created",
        "message": f"🕊️ {memorial.name} 的数字纪念空间已创建。接下来你可以上传照片、语音和故事来完善 TA 的形象。",
    }


@router.get("/list")
async def list_memorials(
    db: AsyncSession = Depends(get_db),
):
    """获取用户的所有怀念角色"""
    import uuid
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    
    result = await db.execute(
        select(MemorialCharacter).where(MemorialCharacter.owner_id == user_id)
    )
    memorials = result.scalars().all()
    
    return {
        "memorials": [
            {
                "id": str(m.id),
                "name": m.name,
                "relation_type": m.relation_type,
                "avatar_url": m.avatar_url,
                "photos_count": len(m.photos),
                "stories_count": len(m.stories),
                "total_conversations": m.total_conversations,
                "created_at": m.created_at.isoformat(),
            }
            for m in memorials
        ]
    }


@router.post("/{memorial_id}/upload-photo")
async def upload_photo(
    memorial_id: str,
    db: AsyncSession = Depends(get_db),
):
    """上传照片"""
    # TODO: 实现文件上传和 GFPGAN 修复
    return {"message": "照片上传功能开发中"}


@router.post("/{memorial_id}/add-story")
async def add_story(
    memorial_id: str,
    story: dict,
    db: AsyncSession = Depends(get_db),
):
    """添加故事/记忆"""
    result = await db.execute(
        select(MemorialCharacter).where(MemorialCharacter.id == memorial_id)
    )
    memorial = result.scalar_one_or_none()
    
    if not memorial:
        raise HTTPException(status_code=404, detail="怀念角色不存在")
    
    stories = memorial.stories or []
    stories.append({
        "content": story.get("content", ""),
        "title": story.get("title", ""),
        "created_at": datetime.utcnow().isoformat(),
    })
    memorial.stories = stories
    
    await db.commit()
    
    return {"message": "故事已保存", "stories_count": len(stories)}
