from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # Стартовые бонусы/штрафы.  
    # Значение может быть отрицательным (штраф).
    strength_bonus = Column(Integer, default=0)
    dexterity_bonus = Column(Integer, default=0)
    constitution_bonus = Column(Integer, default=0)
    intelligence_bonus = Column(Integer, default=0)
    wisdom_bonus = Column(Integer, default=0)
    charisma_bonus = Column(Integer, default=0)

    # Связь с персонажами (обратно из Character.model)
    characters = relationship("Character", back_populates="race_ref")
