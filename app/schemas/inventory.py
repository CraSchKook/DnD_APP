from pydantic import BaseModel
from typing import Optional

class InventoryBase(BaseModel):
    character_id: int
    item_id: int
    quantity: int = 1
    equipped: bool = False

class InventoryCreate(InventoryBase):
    pass

class InventoryRead(InventoryBase):
    id: int

    class Config:
        from_attributes = True
