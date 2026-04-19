"""对话模型"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.engine import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    
    # 消息内容
    role = Column(String(10), nullable=False)  # user/assistant/system
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default="text")  # text/voice/image
    
    # 元数据
    token_count = Column(Integer, default=0)
    model_used = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="conversations")
    character = relationship("Character", back_populates="conversations")
