from pydantic import BaseModel, Field

class Item(BaseModel):
    id: int = Field(..., description="Уникальный ID предмета")
    name: str = Field(..., description="Название предмета")
    description: str | None = Field(None, description="Описание предмета")
    character_id: int = Field(..., description="ID персонажа, которому принадлежит предмет")
