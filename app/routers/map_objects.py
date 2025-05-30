from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database import get_db
from app.models.map_object import MapObject as MapObjectModel
from app.schemas.map_object import MapObjectCreate, MapObjectRead

router = APIRouter(prefix="/map_objects", tags=["Map Objects"])

@router.get("/", response_model=List[MapObjectRead])
async def list_map_objects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MapObjectModel))
    return result.scalars().all()

@router.get("/{object_id}", response_model=MapObjectRead)
async def read_map_object(object_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MapObjectModel).where(MapObjectModel.id == object_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, detail="MapObject not found")
    return obj

@router.post("/", response_model=MapObjectRead, status_code=201)
async def create_map_object(data: MapObjectCreate, db: AsyncSession = Depends(get_db)):
    obj = MapObjectModel(**data.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{object_id}", status_code=204)
async def delete_map_object(object_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MapObjectModel).where(MapObjectModel.id == object_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, detail="MapObject not found")
    await db.delete(obj)
    await db.commit()
