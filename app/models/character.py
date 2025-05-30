# app/models/character.py
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.ability import character_abilities

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)

    attributes = Column(JSON, default={})

    player = relationship("Player", back_populates="characters")
    session = relationship("Session", back_populates="characters")
    inventory_items = relationship(
        "Inventory", back_populates="character", cascade="all, delete-orphan"
    )

    abilities = relationship(
        "Ability",
        secondary=character_abilities,
        back_populates="characters"
    )


# from sqlalchemy import Integer, String, ForeignKey, Column, JSON
# from sqlalchemy.orm import relationship
# from app.database import Base

# class Character(Base):
#     __tablename__ = "characters"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
#     session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)

#     # Базовые характеристики (гибко — через JSON)
#     attributes = Column(JSON, default={})  # Пример: {"strength": 14, "intelligence": 12}
#     abilities = Column(JSON, default=[])   # Пример: ["fireball", "stealth"]

#     # Связи
#     player = relationship("Player", back_populates="characters") # Игрок
#     session = relationship("Session", back_populates="characters") # Сессия
#     inventory_items = relationship("Inventory", back_populates="character", cascade="all, delete-orphan") # Инвентарь
#     abilities = relationship("Ability", back_populates="character", cascade="all, delete-orphan") #способности