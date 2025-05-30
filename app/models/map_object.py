from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class MapObject(Base):
    __tablename__ = "map_objects"

    id = Column(Integer, primary_key=True, index=True)
    map_id = Column(Integer, ForeignKey("maps.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # Например: "trap", "npc", "item"
    position = Column(JSON, nullable=False)  # {'x': 120, 'y': 340}
    properties = Column(JSON, nullable=True)  # Любые доп. данные

    map = relationship("Map", back_populates="objects")
