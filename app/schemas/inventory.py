from pydantic import BaseModel
from typing import Optional

class InventoryBase(BaseModel):
    character_id: int
    capacity: int
    weight_limit: float
    current_weight: float = 0.0

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    capacity: Optional[int] = None
    weight_limit: Optional[float] = None
    current_weight: Optional[float] = None

class Inventory(InventoryBase):
    id: int

    class Config:
        from_attributes = True
