"""对话模型（SQLite 兼容版）"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import relationship
from database.engine import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    character_id = Column(String(50), nullable=False)
    
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(20), default="text")
    
    token_count = Column(Integer, default=0)
    model_used = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
