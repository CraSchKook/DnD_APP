from fastapi import APIRouter, Depends
from app.schemas.item import Item
from app.dependencies.item_db import FakeItemDatabase, get_item_db

router = APIRouter(
    prefix="/items",
    tags=["Items"]
)

@router.get("/", response_model=list[Item])
async def get_items(db: FakeItemDatabase = Depends(get_item_db)):
    return db.list_items()

@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int, db: FakeItemDatabase = Depends(get_item_db)):
    return db.get_item(item_id)

@router.post("/", response_model=Item, status_code=201)
async def create_item(item: Item, db: FakeItemDatabase = Depends(get_item_db)):
    return db.create_item(item)

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, updated: Item, db: FakeItemDatabase = Depends(get_item_db)):
    return db.update_item(item_id, updated)

@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int, db: FakeItemDatabase = Depends(get_item_db)):
    db.delete_item(item_id)
    return
