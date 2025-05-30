# app/models/npc.py
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.ability import npc_abilities

class NPC(Base):
    __tablename__ = "npcs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    race = Column(String, nullable=False)
    profession = Column(String, nullable=False)
    level = Column(Integer, default=1)

    abilities = relationship(
        "Ability",
        secondary=npc_abilities,
        back_populates="npcs"
    )
    inventory = relationship("Inventory", back_populates="npc")

# from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import relationship
# from app.database import Base

# class NPC(Base):
#     __tablename__ = "npcs"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     race = Column(String, nullable=False)
#     profession = Column(String, nullable=False)
#     level = Column(Integer, default=1)

#     # Если есть способности (как у персонажей)
#     abilities = relationship("Ability", secondary="npc_abilities", back_populates="npcs")

#     # Если у NPC может быть инвентарь
#     inventory = relationship("Inventory", back_populates="npc")
