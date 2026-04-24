"""角色模型（SQLite 兼容版）"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database.engine import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    name = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False)
    persona_id = Column(String(50), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    voice_id = Column(String(100), nullable=True)
    
    personality = Column(JSON, nullable=True)
    backstory = Column(Text, nullable=True)
    speaking_style = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=True)
    
    intimacy_level = Column(Float, default=0.0)
    relationship_stage = Column(String(20), default="stranger")
    total_messages = Column(Integer, default=0)
    last_active = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="characters")
    # 简化关系，Conversation.character_id 不是外键（角色由模板ID标识）
    # conversations = relationship("Conversation", lazy="dynamic")
    # memories = relationship("Memory", lazy="dynamic")
