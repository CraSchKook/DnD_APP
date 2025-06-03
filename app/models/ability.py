# app/models/ability.py
from sqlalchemy import Column, Integer, String, Float, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# Association tables for many-to-many relationships
character_abilities = Table(
    'character_abilities',
    Base.metadata,
    Column('character_id', ForeignKey('characters.id', ondelete='CASCADE'), primary_key=True),
    Column('ability_id', ForeignKey('abilities.id', ondelete='CASCADE'), primary_key=True),
)

class Ability(Base):
    __tablename__ = "abilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, default="")
    cooldown = Column(Float, default=0.0)

    # Many-to-Many relationships:
    characters = relationship(
        "Character",
        secondary=character_abilities,
        back_populates="abilities",
        cascade="all, delete"
    )

# from sqlalchemy import Column, Integer, String, ForeignKey, Float
# from sqlalchemy.orm import relationship
# from app.database import Base

# class Ability(Base):
#     __tablename__ = "abilities"

#     id = Column(Integer, primary_key=True, index=True)
#     character_id = Column(Integer, ForeignKey("characters.id"), nullable=False) # привязка
#     name = Column(String, nullable=False) # название
#     description = Column(String, default="") # описание
#     cooldown = Column(Float, default=0.0)  # время перезарядки в секундах

#     character = relationship("Character", back_populates="abilities")
