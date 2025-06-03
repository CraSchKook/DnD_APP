from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Profession(Base):
    __tablename__ = "professions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    hit_die = Column(Integer, default=8)

    strength_bonus = Column(Integer, default=0)
    dexterity_bonus = Column(Integer, default=0)
    constitution_bonus = Column(Integer, default=0)
    intelligence_bonus = Column(Integer, default=0)
    wisdom_bonus = Column(Integer, default=0)
    charisma_bonus = Column(Integer, default=0)

    characters = relationship("Character", back_populates="profession")
