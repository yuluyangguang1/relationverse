"""宠物 API 路由"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from database.engine import get_db
from models.pet import Pet

router = APIRouter()

# 宠物物种配置
SPECIES_CONFIG = {
    "cat": {"name": "猫咪", "emoji": "🐱", "base_personality": ["高冷", "偶尔黏人", "傲娇"]},
    "dog": {"name": "狗狗", "emoji": "🐶", "base_personality": ["热情", "忠诚", "粘人"]},
    "rabbit": {"name": "兔子", "emoji": "🐰", "base_personality": ["温顺", "胆小", "呆萌"]},
    "panda": {"name": "熊猫", "emoji": "🐼", "base_personality": ["懒", "吃货", "反差萌"]},
    "fox": {"name": "狐狸", "emoji": "🦊", "base_personality": ["聪明", "狡黠", "神秘"]},
    "dragon": {"name": "小龙", "emoji": "🐉", "base_personality": ["傲娇", "守护", "强大"]},
    "robot": {"name": "机器宠", "emoji": "🤖", "base_personality": ["理性", "学习型", "进化"]},
}


class CreatePetRequest(BaseModel):
    name: str
    species: str  # cat/dog/rabbit/panda/fox/dragon/robot


class PetActionRequest(BaseModel):
    action: str  # feed/play/clean/talk


@router.get("/species")
async def get_species():
    """获取所有可选宠物物种"""
    species = []
    for sid, cfg in SPECIES_CONFIG.items():
        species.append({
            "id": sid,
            "name": cfg["name"],
            "emoji": cfg["emoji"],
            "personality": cfg["base_personality"],
        })
    return {"species": species}


@router.post("/create")
async def create_pet(
    request: CreatePetRequest,
    db: AsyncSession = Depends(get_db),
):
    """创建新宠物"""
    if request.species not in SPECIES_CONFIG:
        raise HTTPException(status_code=400, detail="未知的宠物物种")
    
    cfg = SPECIES_CONFIG[request.species]
    
    # TODO: 从认证获取用户 ID
    import uuid
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    
    pet = Pet(
        owner_id=user_id,
        name=request.name,
        species=request.species,
        personality_traits=cfg["base_personality"],
    )
    
    db.add(pet)
    await db.commit()
    await db.refresh(pet)
    
    return {
        "id": str(pet.id),
        "name": pet.name,
        "species": pet.species,
        "emoji": cfg["emoji"],
        "hunger": pet.hunger,
        "mood": pet.mood,
        "intimacy": pet.intimacy,
        "speak_level": pet.speak_level,
        "level": pet.level,
    }


@router.post("/{pet_id}/action")
async def pet_action(
    pet_id: str,
    request: PetActionRequest,
    db: AsyncSession = Depends(get_db),
):
    """与宠物互动"""
    result = await db.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    
    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")
    
    now = datetime.utcnow()
    response = {}
    
    if request.action == "feed":
        pet.hunger = min(100, pet.hunger + 30)
        pet.intimacy = min(100, pet.intimacy + 1)
        pet.last_fed = now
        response = {"message": f"🍚 给 {pet.name} 喂了好吃的！", "hunger": pet.hunger}
    
    elif request.action == "play":
        pet.mood = min(100, pet.mood + 20)
        pet.energy = max(0, pet.energy - 15)
        pet.intimacy = min(100, pet.intimacy + 3)
        pet.experience += 10
        pet.last_played = now
        response = {"message": f"🎾 跟 {pet.name} 玩了一会儿！", "mood": pet.mood}
    
    elif request.action == "clean":
        pet.cleanliness = min(100, pet.cleanliness + 40)
        if pet.species == "cat":
            pet.mood = max(0, pet.mood - 5)  # 猫不喜欢洗澡
        pet.last_cleaned = now
        response = {"message": f"🛁 给 {pet.name} 洗了个澡！", "cleanliness": pet.cleanliness}
    
    elif request.action == "talk":
        pet.speak_level = min(100, pet.speak_level + 1)
        pet.intimacy = min(100, pet.intimacy + 2)
        # 根据亲密度生成不同回复
        if pet.intimacy < 20:
            reply = f"{pet.name}: 喵~" if pet.species == "cat" else f"{pet.name}: 汪！"
        elif pet.intimacy < 50:
            reply = f"{pet.name}: 饿饿...想玩..."
        elif pet.intimacy < 80:
            reply = f"{pet.name}: 今天你回来晚了呢，我等了好久。"
        else:
            reply = f"{pet.name}: 你最近是不是不太开心？我感觉你叹气变多了。"
        response = {"message": reply, "speak_level": pet.speak_level}
    
    else:
        raise HTTPException(status_code=400, detail="未知的互动类型")
    
    pet.last_interaction = now
    
    # 检查升级
    if pet.experience >= pet.level * 100:
        pet.level += 1
        response["level_up"] = True
        response["new_level"] = pet.level
    
    await db.commit()
    
    response.update({
        "hunger": round(pet.hunger, 1),
        "cleanliness": round(pet.cleanliness, 1),
        "mood": round(pet.mood, 1),
        "energy": round(pet.energy, 1),
        "intimacy": round(pet.intimacy, 1),
        "speak_level": round(pet.speak_level, 1),
        "level": pet.level,
    })
    
    return response


@router.get("/list")
async def list_pets(
    db: AsyncSession = Depends(get_db),
):
    """获取用户的所有宠物"""
    import uuid
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    
    result = await db.execute(select(Pet).where(Pet.owner_id == user_id))
    pets = result.scalars().all()
    
    return {
        "pets": [
            {
                "id": str(p.id),
                "name": p.name,
                "species": p.species,
                "emoji": SPECIES_CONFIG.get(p.species, {}).get("emoji", "🐾"),
                "hunger": round(p.hunger, 1),
                "cleanliness": round(p.cleanliness, 1),
                "mood": round(p.mood, 1),
                "energy": round(p.energy, 1),
                "intimacy": round(p.intimacy, 1),
                "speak_level": round(p.speak_level, 1),
                "level": p.level,
                "personality_traits": p.personality_traits,
            }
            for p in pets
        ]
    }
