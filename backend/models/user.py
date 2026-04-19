"""用户模型"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.engine import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nickname = Column(String(50), nullable=False)
    avatar = Column(String(500), nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    hashed_password = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String(20), default="free")  # free/silver/gold/diamond
    subscription_expires = Column(DateTime, nullable=True)
    daily_message_count = Column(Integer, default=0)
    daily_message_limit = Column(Integer, default=20)
    last_reset_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    characters = relationship("Character", back_populates="owner", lazy="dynamic")
    pets = relationship("Pet", back_populates="owner", lazy="dynamic")
    memorial_characters = relationship("MemorialCharacter", back_populates="owner", lazy="dynamic")
    conversations = relationship("Conversation", back_populates="user", lazy="dynamic")
