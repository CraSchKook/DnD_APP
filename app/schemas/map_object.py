from pydantic import BaseModel, Field

class MapObject(BaseModel):
    id: int = Field(..., description="Уникальный ID объекта на карте")
    map_id: int = Field(..., description="ID карты, к которой привязан объект")
    type: str = Field(..., description="Тип объекта (стена, дверь, ловушка и т.п.)")
    x: int = Field(..., description="Координата X на сетке карты")
    y: int = Field(..., description="Координата Y на сетке карты")
    state: str | None = Field(None, description="Состояние объекта (например, 'закрыто', 'активно')")
