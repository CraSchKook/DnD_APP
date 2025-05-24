from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship, foreign
from app.database import Base
from app.models.character import Character

class Effect(Base):
    __tablename__ = "effects"

    id          = Column(Integer, primary_key=True, index=True)
    target_type = Column(String, nullable=False)       # "character" или "session"
    target_id   = Column(Integer, nullable=False)      # ID цели
    name        = Column(String, nullable=False)
    duration    = Column(Float, default=0.0)           # длительность в секундах

    # Связь с персонажем (если target_type=="character")
    character = relationship(
        Character,
        primaryjoin="and_(Effect.target_type=='character', foreign(Effect.target_id)==Character.id)",
        viewonly=True,
    )
