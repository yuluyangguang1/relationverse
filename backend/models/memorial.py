"""数字怀念角色模型"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from database.engine import Base


class MemorialCharacter(Base):
    __tablename__ = "memorial_characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 基本信息
    name = Column(String(50), nullable=False)
    relation_type = Column(String(20), nullable=False)  # parent/grandparent/sibling/friend/pet/other
    avatar_url = Column(String(500), nullable=True)
    
    # 记忆素材
    photos = Column(JSON, default=list)  # 照片 URL 列表
    voice_samples = Column(JSON, default=list)  # 语音样本 URL 列表
    stories = Column(JSON, default=list)  # 故事/记忆列表
    chat_records = Column(JSON, default=list)  # 历史聊天记录
    
    # 人设
    personality_desc = Column(Text, nullable=True)  # 性格描述
    catchphrases = Column(JSON, default=list)  # 口头禅
    system_prompt = Column(Text, nullable=True)  # 完整系统提示词
    
    # 语音克隆
    voice_model_id = Column(String(100), nullable=True)  # GPT-SoVITS 模型 ID
    tts_voice_id = Column(String(100), nullable=True)  # TTS 声音 ID
    
    # 互动统计
    total_conversations = Column(Integer, default=0)
    last_active = Column(DateTime, nullable=True)
    
    # 纪念日
    memorial_dates = Column(JSON, default=list)  # 重要日期列表
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    owner = relationship("User", back_populates="memorial_characters")
