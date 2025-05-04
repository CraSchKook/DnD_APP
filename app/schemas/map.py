from pydantic import BaseModel, Field
from typing import Dict, Any

class Map(BaseModel):
    id: int = Field(..., description="Уникальный ID карты")
    session_id: int = Field(..., description="ID сессии, к которой привязана карта")
    layout: Dict[str, Any] = Field(
        ...,
        description="Структура карты (например, JSON-описание тайлов и объектов)"
    )
