from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models.character import Character as CharacterModel

from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterRead
from app.schemas.inventory import InventoryRead
from app.models.inventory import Inventory as InventoryModel

router = APIRouter(
    prefix="/characters",
    tags=["Characters"]
)

@router.get("/", response_model=List[CharacterRead])
async def list_characters(db: AsyncSession = Depends(get_db)):
    """
    Вернуть всех персонажей вместе с их способностями.
    Загрузка abilities через selectinload, чтобы избежать ошибок ленивой загрузки.
    """
    result = await db.execute(
        select(CharacterModel)
        .options(selectinload(CharacterModel.abilities))
    )
    return result.scalars().all()

@router.get("/{character_id}", response_model=CharacterRead)
async def get_character(character_id: int, db: AsyncSession = Depends(get_db)):
    """
    Вернуть одного персонажа по ID, вместе с его способностями.
    """
    result = await db.execute(
        select(CharacterModel)
        .where(CharacterModel.id == character_id)
        .options(selectinload(CharacterModel.abilities))
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@router.post("/", response_model=CharacterRead, status_code=201)
async def create_character(new_char: CharacterCreate, db: AsyncSession = Depends(get_db)):
    """
    Создать нового персонажа.
    """
    character = CharacterModel(**new_char.dict())
    db.add(character)
    await db.commit()
    await db.refresh(character)
    return character

@router.put("/{character_id}", response_model=CharacterRead)
async def update_character(
    character_id: int,
    data: CharacterUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить данные персонажа.
    """
    result = await db.execute(select(CharacterModel).where(CharacterModel.id == character_id))
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(character, field, value)

    await db.commit()
    await db.refresh(character)
    return character

@router.delete("/{character_id}", status_code=204)
async def delete_character(character_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удалить персонажа.
    """
    result = await db.execute(select(CharacterModel).where(CharacterModel.id == character_id))
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    await db.delete(character)
    await db.commit()
    return

@router.get("/{character_id}/inventory", response_model=List[InventoryRead])
async def character_inventory(character_id: int, db: AsyncSession = Depends(get_db)):
    """
    Вернуть список предметов в инвентаре данного персонажа.
    """
    # Проверяем существование персонажа
    res_char = await db.execute(select(CharacterModel).where(CharacterModel.id == character_id))
    char = res_char.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    # Возвращаем инвентарь этого персонажа
    res_inv = await db.execute(
        select(InventoryModel)
        .where(InventoryModel.character_id == character_id)
    )
    return res_inv.scalars().all()
