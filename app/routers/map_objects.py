from fastapi import APIRouter, Depends
from app.schemas.map_object import MapObject
from app.dependencies.map_object_db import FakeMapObjectDatabase, get_map_object_db

router = APIRouter(
    prefix="/map-objects",
    tags=["MapObjects"]
)

@router.get("/", response_model=list[MapObject])
async def get_map_objects(db: FakeMapObjectDatabase = Depends(get_map_object_db)):
    return db.list_objects()

@router.get("/{object_id}", response_model=MapObject)
async def get_map_object(object_id: int, db: FakeMapObjectDatabase = Depends(get_map_object_db)):
    return db.get_object(object_id)

@router.post("/", response_model=MapObject, status_code=201)
async def create_map_object(obj: MapObject, db: FakeMapObjectDatabase = Depends(get_map_object_db)):
    return db.create_object(obj)

@router.put("/{object_id}", response_model=MapObject)
async def update_map_object(object_id: int, updated: MapObject, db: FakeMapObjectDatabase = Depends(get_map_object_db)):
    return db.update_object(object_id, updated)

@router.delete("/{object_id}", status_code=204)
async def delete_map_object(object_id: int, db: FakeMapObjectDatabase = Depends(get_map_object_db)):
    db.delete_object(object_id)
    return
