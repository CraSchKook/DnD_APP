# app/models/character.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.ability import character_abilities

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    is_npc = Column(Boolean, default=False, nullable=False)  # NPC или нет

    player_id = Column(Integer, ForeignKey("players.id"), nullable=True)  # может быть null у NPC
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)

    race_id = Column(Integer, ForeignKey("races.id"), nullable=False)
    race = relationship("Race", back_populates="characters")

    profession_id = Column(Integer, ForeignKey("professions.id")) # НА САМОМ ДЕЛЕ ЭТО КЛАСС
    profession = relationship("Profession", back_populates="characters") # НА САМОМ ДЕЛЕ ЭТО КЛАСС

    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)
    level = relationship("Level", back_populates="characters")

    avatar_url = Column(String, nullable=True)  # новое поле

    # Здесь будут уже ФИНАЛЬНЫЕ ХАРАКТЕРИСТИКИ после применения всех бонусов и распределения:
    hp = Column(Integer, default=10)
    armor = Column(Integer, default=10) # просто есть
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)

    shards = Column(JSON, default=lambda: {
        "red": 0,
        "green": 0,
        "blue": 0,
        "black": 0,
        "white": 0
    })

    inventory_items = relationship(
        "Inventory", back_populates="character", cascade="all, delete-orphan"
    )

    abilities = relationship(
        "Ability",
        secondary=character_abilities,
        back_populates="characters"
    )

    player = relationship("Player", back_populates="characters")
    session = relationship("Session", back_populates="characters")
