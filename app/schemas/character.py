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
    ability_ids: List[int] = Field(
        default_factory=list,
        description="Список ID способностей для присвоения персонажу"
    )

class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Новое имя персонажа")
    session_id: Optional[int] = Field(None, description="Обновлённый ID сессии")
    attributes: Optional[Dict[str, int]] = Field(
        None,
        description="Обновлённые характеристики персонажа"
    )
    ability_ids: Optional[List[int]] = Field(
        None,
        description="Обновлённый список ID способностей для персонажа"
    )

class CharacterRead(CharacterBase):
    id: int = Field(..., description="Уникальный ID персонажа")
    abilities: List[AbilityRead] = Field(
        default_factory=list,
        description="Список способностей персонажа"
    )

    class Config:
        orm_mode = True