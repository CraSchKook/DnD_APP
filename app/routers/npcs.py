from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models.npc import NPC as NPCModel
from app.schemas.npc import NPCCreate, NPCUpdate, NPCRead
from app.schemas.inventory import InventoryRead
from app.models.inventory import Inventory as InventoryModel

router = APIRouter(
    prefix="/npcs",
    tags=["NPCs"]
)

@router.get("/", response_model=List[NPCRead])
async def list_npcs(db: AsyncSession = Depends(get_db)):
    """
    Получить список всех NPC с загруженными способностями.
    """
    result = await db.execute(
        select(NPCModel)
        .options(selectinload(NPCModel.abilities))
    )
    return result.scalars().all()

@router.get("/{npc_id}", response_model=NPCRead)
async def get_npc(npc_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить одного NPC по ID.
    """
    result = await db.execute(
        select(NPCModel)
        .where(NPCModel.id == npc_id)
        .options(selectinload(NPCModel.abilities))
    )
    npc = result.scalar_one_or_none()
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")
    return npc

@router.post("/", response_model=NPCRead, status_code=201)
async def create_npc(npc_data: NPCCreate, db: AsyncSession = Depends(get_db)):
    """
    Создать нового NPC.
    """
    npc = NPCModel(**npc_data.dict())
    db.add(npc)
    await db.commit()
    await db.refresh(npc)
    return npc

@router.put("/{npc_id}", response_model=NPCRead)
async def update_npc(npc_id: int, data: NPCUpdate, db: AsyncSession = Depends(get_db)):
    """
    Обновить данные NPC.
    """
    result = await db.execute(select(NPCModel).where(NPCModel.id == npc_id))
    npc = result.scalar_one_or_none()
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(npc, field, value)

    await db.commit()
    await db.refresh(npc)
    return npc

@router.delete("/{npc_id}", status_code=204)
async def delete_npc(npc_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удалить NPC.
    """
    result = await db.execute(select(NPCModel).where(NPCModel.id == npc_id))
    npc = result.scalar_one_or_none()
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")

    await db.delete(npc)
    await db.commit()

@router.get("/{npc_id}/inventory", response_model=List[InventoryRead])
async def npc_inventory(npc_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить инвентарь NPC.
    """
    res_npc = await db.execute(select(NPCModel).where(NPCModel.id == npc_id))
    npc = res_npc.scalar_one_or_none()
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")

    res_inv = await db.execute(
        select(InventoryModel)
        .where(InventoryModel.npc_id == npc_id)
    )
    return res_inv.scalars().all()
