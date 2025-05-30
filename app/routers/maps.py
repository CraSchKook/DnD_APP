from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database import get_db
from app.models.map import Map as MapModel
from app.schemas.map import MapCreate, MapRead

router = APIRouter(prefix="/maps", tags=["Maps"])

@router.get("/", response_model=List[MapRead])
async def list_maps(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MapModel))
    return result.scalars().all()

@router.get("/{map_id}", response_model=MapRead)
async def read_map(map_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MapModel).where(MapModel.id == map_id))
    map_obj = result.scalar_one_or_none()
    if not map_obj:
        raise HTTPException(404, detail="Map not found")
    return map_obj

@router.post("/", response_model=MapRead, status_code=201)
async def create_map(data: MapCreate, db: AsyncSession = Depends(get_db)):
    map_obj = MapModel(**data.dict())
    db.add(map_obj)
    await db.commit()
    await db.refresh(map_obj)
    return map_obj

@router.delete("/{map_id}", status_code=204)
async def delete_map(map_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MapModel).where(MapModel.id == map_id))
    map_obj = result.scalar_one_or_none()
    if not map_obj:
        raise HTTPException(404, detail="Map not found")
    await db.delete(map_obj)
    await db.commit()
