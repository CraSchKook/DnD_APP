from sqlalchemy import Column, Integer, String, Float, JSON
from app.database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    weight = Column(Float, default=0.0)
    properties = Column(JSON, default={})  
    # Пример properties: {"damage": "1d8", "type": "melee"}
