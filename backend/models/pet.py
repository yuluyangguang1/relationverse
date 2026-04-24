"""宠物模型（SQLite 兼容版）"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database.engine import Base


class Pet(Base):
    __tablename__ = "pets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    name = Column(String(50), nullable=False)
    species = Column(String(20), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    
    hunger = Column(Float, default=80.0)
    cleanliness = Column(Float, default=80.0)
    mood = Column(Float, default=80.0)
    energy = Column(Float, default=80.0)
    intimacy = Column(Float, default=0.0)
    speak_level = Column(Float, default=0.0)
    
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    
    personality_traits = Column(JSON, default=list)
    
    last_fed = Column(DateTime, nullable=True)
    last_played = Column(DateTime, nullable=True)
    last_cleaned = Column(DateTime, nullable=True)
    last_interaction = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="pets")
