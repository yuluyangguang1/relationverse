"""记忆模型"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from database.engine import Base


class Memory(Base):
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id"), nullable=True)
    
    # 记忆内容
    content = Column(Text, nullable=False)
    memory_type = Column(String(20), default="fact")  # fact/emotion/event/reminder
    importance = Column(Float, default=0.5)  # 0-1 重要度
    
    # 向量存储引用
    embedding_id = Column(String(100), nullable=True)  # Qdrant 中的向量 ID
    
    # 标签
    tags = Column(ARRAY(String), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    accessed_at = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=0)

    # 关系
    character = relationship("Character", back_populates="memories")
