"""宠物模型"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.engine import Base


class Pet(Base):
    __tablename__ = "pets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 基本信息
    name = Column(String(50), nullable=False)
    species = Column(String(20), nullable=False)  # cat/dog/rabbit/panda/fox/dragon/robot
    avatar_url = Column(String(500), nullable=True)
    
    # 属性值 (0-100)
    hunger = Column(Float, default=80.0)  # 饥饿值
    cleanliness = Column(Float, default=80.0)  # 清洁值
    mood = Column(Float, default=80.0)  # 心情值
    energy = Column(Float, default=80.0)  # 精力值
    intimacy = Column(Float, default=0.0)  # 亲密度
    speak_level = Column(Float, default=0.0)  # 说话能力
    
    # 等级
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    
    # 性格演化
    personality_traits = Column(JSON, default=list)  # 动态性格标签
    
    # 状态
    last_fed = Column(DateTime, nullable=True)
    last_played = Column(DateTime, nullable=True)
    last_cleaned = Column(DateTime, nullable=True)
    last_interaction = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    owner = relationship("User", back_populates="pets")
