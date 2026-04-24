"""数字怀念角色模型（SQLite 兼容版）"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Float, Integer
from sqlalchemy.orm import relationship
from database.engine import Base


class MemorialCharacter(Base):
    __tablename__ = "memorial_characters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    name = Column(String(50), nullable=False)
    relation_type = Column(String(20), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    
    photos = Column(JSON, default=list)
    voice_samples = Column(JSON, default=list)
    stories = Column(JSON, default=list)
    chat_records = Column(JSON, default=list)
    
    personality_desc = Column(Text, nullable=True)
    catchphrases = Column(JSON, default=list)
    system_prompt = Column(Text, nullable=True)
    
    voice_model_id = Column(String(100), nullable=True)
    tts_voice_id = Column(String(100), nullable=True)
    
    total_conversations = Column(Integer, default=0)
    last_active = Column(DateTime, nullable=True)
    
    memorial_dates = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="memorial_characters")
