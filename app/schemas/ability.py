from pydantic import BaseModel, Field

class Ability(BaseModel):
    id: int = Field(..., description="Уникальный ID способности")
    name: str = Field(..., description="Название способности")
    description: str | None = Field(None, description="Описание способности")
    cooldown: int = Field(..., description="Время восстановления (в секундах)")
    character_id: int = Field(..., description="ID персонажа-владельца способности")
