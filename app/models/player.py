from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    username = Column(String, nullable=True)
    
    role = Column(String, default="player", nullable=False)  # может ли быть мастером
    active_as = Column(String, default="player", nullable=False)  # сейчас играет как кто

    characters = relationship("Character", back_populates="player", cascade="all, delete-orphan")
