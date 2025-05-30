from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class MapBase(BaseModel):
    name: str = Field(..., description="Название карты")
    image_url: str = Field(..., description="URL изображения карты")
    layout: Optional[Dict[str, Any]] = Field(
        None, description="Структура карты в формате JSON (например, тайлы, сетка)"
    )

class MapCreate(MapBase):
    pass

class MapRead(MapBase):
    id: int = Field(..., description="Уникальный ID карты")

    class Config:
        from_attributes = True
