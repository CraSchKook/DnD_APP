# app/schemas/inventory.py

from pydantic import BaseModel, Field
from typing import List

from app.schemas.item import ItemRead  # DTO вашего предмета

class InventoryBase(BaseModel):
    character_id: int = Field(..., description="ID персонажа")
    item_id: int = Field(..., description="ID предмета")
    quantity: int = Field(1, description="Количество предметов")
    equipped: bool = Field(False, description="Надето ли (True) или лежит в рюкзаке (False)")

class InventoryCreate(InventoryBase):
    pass

class InventoryItemRead(BaseModel):
    id: int = Field(..., description="ID записи в таблице inventory")
    quantity: int = Field(..., description="Количество данного предмета")
    equipped: bool = Field(..., description="Надет ли предмет")
    item: ItemRead = Field(..., description="Детали предмета")

    class Config:
        orm_mode = True
        model_config = {"from_attributes": True}

class InventoryGroup(BaseModel):
    id: int = Field(..., description="ID группы (совпадает с character_id)")
    character_id: int = Field(..., description="ID персонажа")
    items: List[InventoryItemRead] = Field(
        default_factory=list,
        description="Список вещей с вложенными данными предметов"
    )

    class Config:
        orm_mode = True
        model_config = {"from_attributes": True}
