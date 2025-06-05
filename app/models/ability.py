# app/models/ability.py
from sqlalchemy import Column, Integer, String, Float, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# Association tables for many-to-many relationships
character_abilities = Table(
    'character_abilities',
    Base.metadata,
    Column('character_id', ForeignKey('characters.id', ondelete='CASCADE'), primary_key=True),
    Column('ability_id', ForeignKey('abilities.id', ondelete='CASCADE'), primary_key=True),
)

# Новая таблица: Race ↔ Ability
race_abilities = Table(
    'race_abilities',
    Base.metadata,
    Column('race_id', ForeignKey('races.id', ondelete='CASCADE'), primary_key=True),
    Column('ability_id', ForeignKey('abilities.id', ondelete='CASCADE'), primary_key=True),
)

# Новая таблица: Profession ↔ Ability
profession_abilities = Table(
    'profession_abilities',
    Base.metadata,
    Column('profession_id', ForeignKey('professions.id', ondelete='CASCADE'), primary_key=True),
    Column('ability_id', ForeignKey('abilities.id', ondelete='CASCADE'), primary_key=True),
)

class Ability(Base):
    __tablename__ = "abilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, default="")
    cooldown = Column(Float, default=0.0)

    # Many-to-Many: Character ↔ Ability
    characters = relationship(
        "Character",
        secondary=character_abilities,
        back_populates="abilities",
        cascade="all, delete"
    )

    # Many-to-Many: Race ↔ Ability (теперь можем проверять расовые ограничения)
    races = relationship(
        "Race",
        secondary=race_abilities,
        back_populates="abilities"
    )

    # Many-to-Many: Profession ↔ Ability (для классовых ограничений)
    professions = relationship(
        "Profession",
        secondary=profession_abilities,
        back_populates="abilities"
    )