from pydantic import BaseModel, Field
from typing import Dict

class NPC(BaseModel):
    id: int = Field(..., description="Уникальный ID NPC")
    session_id: int = Field(..., description="ID сессии, к которой относится NPC")
    name: str = Field(..., description="Имя NPC")
    stats: Dict[str, int] = Field(
        ..., 
        description="Словарь характеристик, например {'hp': 10, 'ac': 12}"
    )
    x: int = Field(..., description="Координата X на карте")
    y: int = Field(..., description="Координата Y на карте")
