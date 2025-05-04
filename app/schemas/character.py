from pydantic import BaseModel, Field
from typing import Dict

class Character(BaseModel):
    id: int = Field(..., description="Уникальный ID персонажа")
    session_id: int = Field(..., description="ID сессии, к которой привязан персонаж")
    player_id: int = Field(..., description="ID игрока-владельца этого персонажа")
    name: str = Field(..., description="Имя персонажа")
    stats: Dict[str, int] = Field(
        ..., 
        description="Словарь базовых характеристик, например {'strength': 10, 'dexterity': 12}"
    )
    hp: int = Field(..., description="Текущее здоровье персонажа")
