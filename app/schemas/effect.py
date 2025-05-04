from pydantic import BaseModel, Field
from datetime import timedelta

class Effect(BaseModel):
    id: int = Field(..., description="Уникальный ID эффекта")
    target_type: str = Field(..., description="Куда применён эффект (Player, Character, NPC)")
    target_id: int = Field(..., description="ID сущности, к которой применён эффект")
    name: str = Field(..., description="Название эффекта (например, 'слепота')")
    duration: int = Field(..., description="Длительность эффекта в секундах")
