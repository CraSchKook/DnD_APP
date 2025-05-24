from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.inventory import Inventory as InventoryModel
from app.schemas.inventory import InventoryCreate, InventoryRead

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/", response_model=list[InventoryRead])
async def list_inventory(
    character_id: Optional[int] = Query(None, description="ID персонажа для фильтрации"),
    db: AsyncSession = Depends(get_db)
):
    """
    Если передан character_id — вернёт только предметы этого персонажа,
    иначе — без фильтрации, все записи из inventory.
    """
    stmt = select(InventoryModel)
    if character_id is not None:
        stmt = stmt.where(InventoryModel.character_id == character_id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/", response_model=list[InventoryRead])
async def list_inventory(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InventoryModel))
    return result.scalars().all()

@router.post("/", response_model=InventoryRead, status_code=201)
async def add_to_inventory(data: InventoryCreate, db: AsyncSession = Depends(get_db)):
    inv = InventoryModel(**data.dict())
    db.add(inv)
    await db.commit()
    await db.refresh(inv)
    return inv

@router.get("/{inv_id}", response_model=InventoryRead)
async def read_inventory(inv_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InventoryModel).where(InventoryModel.id == inv_id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(404, "Not found")
    return inv

@router.delete("/{inv_id}", status_code=204)
async def remove_from_inventory(inv_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(InventoryModel).where(InventoryModel.id == inv_id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(404, "Not found")
    await db.delete(inv)
    await db.commit()
