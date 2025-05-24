from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Ability(Base):
    __tablename__ = "abilities"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False) # привязка
    name = Column(String, nullable=False) # название
    description = Column(String, default="") # описание
    cooldown = Column(Float, default=0.0)  # время перезарядки в секундах

    character = relationship("Character", back_populates="abilities")
