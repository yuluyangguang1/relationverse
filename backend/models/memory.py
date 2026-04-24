"""记忆模型（SQLite 兼容版）"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Integer, JSON
from sqlalchemy.orm import relationship
from database.engine import Base


class Memory(Base):
    __tablename__ = "memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    character_id = Column(String(50), nullable=True)
    
    content = Column(Text, nullable=False)
    memory_type = Column(String(20), default="fact")
    importance = Column(Float, default=0.5)
    
    embedding_id = Column(String(100), nullable=True)
    
    tags = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    accessed_at = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=0)

    # 关系（简化，不依赖Character表）
    # character = relationship("Character", back_populates="memories")
