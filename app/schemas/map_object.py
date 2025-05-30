from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class MapObjectBase(BaseModel):
    name: str = Field(..., description="Название объекта на карте")
    type: str = Field(..., description="Тип объекта (например, 'стена', 'дверь', 'ловушка')")
    position: Dict[str, int] = Field(..., description="Позиция объекта на карте: {'x': int, 'y': int}")
    properties: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Дополнительные свойства объекта (например, состояние, взаимодействие)"
    )

class MapObjectCreate(MapObjectBase):
    map_id: int = Field(..., description="ID карты, к которой привязан объект")

class MapObjectRead(MapObjectBase):
    id: int = Field(..., description="Уникальный ID объекта")
    map_id: int = Field(..., description="ID карты, к которой привязан объект")

    class Config:
        from_attributes = True
