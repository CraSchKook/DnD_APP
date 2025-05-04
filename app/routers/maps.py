from fastapi import APIRouter, Depends
from app.schemas.map import Map
from app.dependencies.map_db import FakeMapDatabase, get_map_db

router = APIRouter(
    prefix="/maps",
    tags=["Maps"]
)

@router.get("/", response_model=list[Map])
async def get_maps(db: FakeMapDatabase = Depends(get_map_db)):
    return db.list_maps()

@router.get("/{map_id}", response_model=Map)
async def get_map(map_id: int, db: FakeMapDatabase = Depends(get_map_db)):
    return db.get_map(map_id)

@router.post("/", response_model=Map, status_code=201)
async def create_map(map_obj: Map, db: FakeMapDatabase = Depends(get_map_db)):
    return db.create_map(map_obj)

@router.put("/{map_id}", response_model=Map)
async def update_map(map_id: int, updated: Map, db: FakeMapDatabase = Depends(get_map_db)):
    return db.update_map(map_id, updated)

@router.delete("/{map_id}", status_code=204)
async def delete_map(map_id: int, db: FakeMapDatabase = Depends(get_map_db)):
    db.delete_map(map_id)
    return
