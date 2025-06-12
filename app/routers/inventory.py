# app/routers/inventory.py

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload

from app.database import get_db
from app.models.inventory import Inventory as InventoryModel
from app.models.character import Character as CharacterModel
from app.schemas.inventory import InventoryCreate, InventoryItemRead
from app.core.auth import get_current_user
from app.models.player import Player as PlayerModel

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/me", response_model=List[InventoryItemRead])
async def list_my_inventory(
    db: AsyncSession = Depends(get_db),
    current_user: PlayerModel = Depends(get_current_user)
):
    """
    Вернуть все записи инвентаря персонажей текущего игрока.
    Мастер видит инвентари всех.
    """
    stmt = select(InventoryModel).options(selectinload(InventoryModel.item))
    if current_user.active_as != "master":
        # Фильтруем по персонажам, принадлежащим текущему игроку
        stmt = stmt.join(CharacterModel).where(CharacterModel.player_id == current_user.id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/", response_model=List[InventoryItemRead])
async def list_inventory(
    character_id: Optional[int] = Query(None, description="ID персонажа для фильтрации"),
    db: AsyncSession = Depends(get_db),
    current_user: PlayerModel = Depends(get_current_user)
):
    """
    Если указан character_id — вернёт вещи этого персонажа (любого) для просмотра/воровства;.
    Если не указан:
      - мастер получит все записи inventory;
      - обычный игрок — только свои (как /me).
    """
    stmt = select(InventoryModel).options(selectinload(InventoryModel.item))
    if character_id is not None:
        # любой может посмотреть чужой инвентарь
        stmt = stmt.where(InventoryModel.character_id == character_id)
    else:
        # без фильтра мастеру — всё, остальным — только свои
        if current_user.active_as != "master":
            stmt = stmt.join(CharacterModel).where(CharacterModel.player_id == current_user.id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=InventoryItemRead, status_code=status.HTTP_201_CREATED)
async def add_to_inventory(
    data: InventoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: PlayerModel = Depends(get_current_user)
):
    """
    Добавить предмет в инвентарь.
    Обычный игрок может добавить только себе (data.character_id == его ID персонажа).
    Мастер — в любой.
    """
    if current_user.active_as != "master":
        # проверяем, что переданный character_id принадлежит ему
        res = await db.execute(select(CharacterModel).where(
            (CharacterModel.id == data.character_id) &
            (CharacterModel.player_id == current_user.id)
        ))
        if not res.scalar_one_or_none():
            raise HTTPException(status_code=403, detail="Cannot add to someone else's inventory")

    inv = InventoryModel(**data.dict())
    db.add(inv)
    await db.commit()
    await db.refresh(inv)
    # подгружаем item
    await db.refresh(inv, ["item"])
    return inv


@router.delete("/{inv_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_inventory(
    inv_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: PlayerModel = Depends(get_current_user)
):
    """
    Удалить запись из инвентаря.
    Обычный игрок — только свои; мастер — любые.
    """
    res = await db.execute(
        select(InventoryModel).where(InventoryModel.id == inv_id).options(selectinload(InventoryModel.item))
    )
    inv = res.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Not found")

    if current_user.active_as != "master":
        # проверяем владельца
        if inv.character_id:
            res_char = await db.execute(select(CharacterModel).where(
                (CharacterModel.id == inv.character_id) &
                (CharacterModel.player_id == current_user.id)
            ))
            if not res_char.scalar_one_or_none():
                raise HTTPException(status_code=403, detail="Cannot remove from someone else's inventory")

    await db.delete(inv)
    await db.commit()