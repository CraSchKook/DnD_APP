from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # --------------- Существующие бонусы/штрафы ---------------
    strength_bonus = Column(Integer, default=0)
    dexterity_bonus = Column(Integer, default=0)
    constitution_bonus = Column(Integer, default=0)
    intelligence_bonus = Column(Integer, default=0)
    wisdom_bonus = Column(Integer, default=0)
    charisma_bonus = Column(Integer, default=0)

    # --------------- Новые поля для расширенной логики ---------------
    extra_hp = Column(Integer, default=2)
    movement_speed = Column(Integer, default=30)  # скорость перемещения (в футах)
    night_vision = Column(Boolean, default=False)  # ночное зрение
    resistances = Column(JSON, default=list)  # устойчивости к типам урона/эффектов, пример: ["fire", "cold"]
    languages = Column(JSON, default=list)    # известные языки, пример: ["Common", "Elvish"]
    traits = Column(JSON, default=list)       # уникальные черты (пассивки), пример: ["Lucky", "Brave"]

    # Связь с персонажами (обратно из Character.model)
    characters = relationship("Character", back_populates="race")

    # Новое поле: какие способности доступны этой расе
    abilities = relationship(
        "Ability",
        secondary="race_abilities",   # строка-имя таблицы
        back_populates="races"
    )
