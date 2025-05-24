# app/schemas/character.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from app.schemas.ability import AbilityRead

class CharacterBase(BaseModel):
    name: str = Field(..., description="Имя персонажа")
    player_id: int = Field(..., description="ID игрока-владельца")
    session_id: Optional[int] = Field(None, description="ID сессии, если привязан")
    attributes: Dict[str, int] = Field(..., description="Характеристики персонажа")

class CharacterCreate(CharacterBase):
    pass

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    session_id: Optional[int] = None
    attributes: Optional[Dict[str, int]] = None

class CharacterRead(CharacterBase):
    id: int = Field(..., description="Уникальный ID персонажа")
    abilities: List[AbilityRead] = Field(
        default_factory=list,
        description="Список способностей персонажа"
    )

    class Config:
        from_attributes = True