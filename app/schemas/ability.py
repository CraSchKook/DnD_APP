# app/schemas/ability.py
from pydantic import BaseModel
from typing import Optional

class AbilityBase(BaseModel):
    name: str
    description: Optional[str] = None
    cooldown: float = 0.0
    character_id: int

class AbilityCreate(AbilityBase):
    pass

class AbilityRead(AbilityBase):
    id: int

    class Config:
        from_attributes = True

class AbilityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cooldown: Optional[float] = None