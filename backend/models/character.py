"""角色模型"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.engine import Base


class Character(Base):
    __tablename__ = "characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 基本信息
    name = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False)  # girlfriend/boyfriend/friend/family/mentor/fantasy
    persona_id = Column(String(50), nullable=False)  # 人设模板 ID
    avatar_url = Column(String(500), nullable=True)
    voice_id = Column(String(100), nullable=True)  # TTS 声音 ID
    
    # 人设配置
    personality = Column(JSON, nullable=True)  # 性格标签
    backstory = Column(Text, nullable=True)  # 背景故事
    speaking_style = Column(Text, nullable=True)  # 说话风格
    system_prompt = Column(Text, nullable=True)  # 完整系统提示词
    
    # 关系状态
    intimacy_level = Column(Float, default=0.0)  # 亲密度 0-100
    relationship_stage = Column(String(20), default="stranger")  # stranger/friend/flirting/lover/deep_love/soulmate
    total_messages = Column(Integer, default=0)
    last_active = Column(DateTime, nullable=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    owner = relationship("User", back_populates="characters")
    conversations = relationship("Conversation", back_populates="character", lazy="dynamic")
    memories = relationship("Memory", back_populates="character", lazy="dynamic")
