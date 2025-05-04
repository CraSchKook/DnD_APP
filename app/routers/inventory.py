from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.dependencies.db import FakeDatabase, get_db
from app.schemas.inventory import Inventory, InventoryCreate, InventoryUpdate
from app.models.inventory import Inventory as InventoryModel

router = APIRouter(prefix="/inventories", tags=["Inventories"])

@router.post("/", response_model=Inventory)
def create_inventory(inventory: InventoryCreate, db: FakeDatabase = Depends(get_db)):
    new_id = len(db.inventories) + 1
    new_inventory = InventoryModel(
        id=new_id,
        character_id=inventory.character_id,
        capacity=inventory.capacity,
        weight_limit=inventory.weight_limit,
        current_weight=inventory.current_weight,
    )
    db.inventories.append(new_inventory)
    return new_inventory

@router.get("/", response_model=List[Inventory])
def get_inventories(db: FakeDatabase = Depends(get_db)):
    return db.inventories

@router.get("/{inventory_id}", response_model=Inventory)
def get_inventory(inventory_id: int, db: FakeDatabase = Depends(get_db)):
    inventory = next((i for i in db.inventories if i.id == inventory_id), None)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

@router.put("/{inventory_id}", response_model=Inventory)
def update_inventory(inventory_id: int, inventory_update: InventoryUpdate, db: FakeDatabase = Depends(get_db)):
    inventory = next((i for i in db.inventories if i.id == inventory_id), None)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    if inventory_update.capacity is not None:
        inventory.capacity = inventory_update.capacity
    if inventory_update.weight_limit is not None:
        inventory.weight_limit = inventory_update.weight_limit
    if inventory_update.current_weight is not None:
        inventory.current_weight = inventory_update.current_weight
    return inventory

@router.delete("/{inventory_id}")
def delete_inventory(inventory_id: int, db: FakeDatabase = Depends(get_db)):
    inventory = next((i for i in db.inventories if i.id == inventory_id), None)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    db.inventories.remove(inventory)
    return {"detail": "Inventory deleted"}
