from pydantic import BaseModel
from typing import Optional, Dict, Any

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    weight: float = 0.0
    properties: Dict[str, Any] = {}

class ItemCreate(ItemBase):
    pass

class ItemRead(ItemBase):
    id: int

    class Config:
        from_attributes = True
