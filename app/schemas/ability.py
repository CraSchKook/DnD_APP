# app/schemas/ability.py
from pydantic import BaseModel
from typing import Optional, List

class AbilityBase(BaseModel):
    name: str
    description: Optional[str] = None
    cooldown: float = 0.0

class AbilityCreate(AbilityBase):
    character_ids: Optional[List[int]] = []
    npc_ids: Optional[List[int]] = []

class AbilityRead(AbilityBase):
    id: int
    character_ids: List[int] = []
    npc_ids: List[int] = []

    class Config:
        orm_mode = True

class AbilityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cooldown: Optional[float] = None
    character_ids: Optional[List[int]] = None
    npc_ids: Optional[List[int]] = None