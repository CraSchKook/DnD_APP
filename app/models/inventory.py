# app/models/inventory.py
from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete='CASCADE'), nullable=True)
    npc_id = Column(Integer, ForeignKey("npcs.id", ondelete='CASCADE'), nullable=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, default=1)
    equipped = Column(Boolean, default=False)

    # Отношения
    character = relationship("Character", back_populates="inventory_items")
    npc = relationship("NPC", back_populates="inventory")
    item = relationship("Item")