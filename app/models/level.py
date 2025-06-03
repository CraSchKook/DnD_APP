from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True)  
    # Здесь id = номер уровня (1, 2, 3 и т. д.)

    # Описание того, что даёт этот уровень:
    hp_increase = Column(Integer, default=5, nullable=False)
    bonus_attribute = Column(String, default="None", nullable=True)
    description = Column(String, default="", nullable=True)

    # Можно хранить отношение к персонажам, но необязательно
    characters = relationship("Character", back_populates="level")
