from pydantic import BaseModel, Field
from typing import Optional

class NPCCreate(BaseModel):
    name: str = Field(..., description="Имя NPC")
    race: str = Field(..., description="Раса NPC")
    profession: str = Field(..., description="Профессия или роль NPC")
    level: int = Field(1, description="Уровень NPC")

class NPCUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Имя NPC")
    race: Optional[str] = Field(None, description="Раса NPC")
    profession: Optional[str] = Field(None, description="Профессия или роль NPC")
    level: Optional[int] = Field(None, description="Уровень NPC")

class NPCRead(NPCCreate):
    id: int = Field(..., description="ID NPC")

    class Config:
        from_attributes = True