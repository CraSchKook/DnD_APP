# app/routers/characters.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models.character import Character as CharacterModel
from app.models.ability import Ability as AbilityModel
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
    """
    result = await db.execute(
        select(CharacterModel)
        .options(selectinload(CharacterModel.abilities))
    )
    characters = result.scalars().all()
    return characters

@router.get("/{character_id}", response_model=CharacterRead)
async def get_character(character_id: int, db: AsyncSession = Depends(get_db)):
    """
    Вернуть одного персонажа по ID вместе с его способностями.
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
    Создать нового персонажа с возможностью назначения способностей.
    """
    # Создаём персонажа на основе базовых данных
    character = CharacterModel(
        name=new_char.name,
        player_id=new_char.player_id,
        session_id=new_char.session_id,
        attributes=new_char.attributes
    )
    # Назначение способностей, если переданы
    if new_char.ability_ids:
        result = await db.execute(
            select(AbilityModel).where(AbilityModel.id.in_(new_char.ability_ids))
        )
        character.abilities = result.scalars().all()
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
    Обновить данные персонажа и его список способностей.
    """
    result = await db.execute(
        select(CharacterModel)
        .where(CharacterModel.id == character_id)
        .options(selectinload(CharacterModel.abilities))
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    # Обновляем простые поля
    update_data = data.dict(exclude_unset=True, exclude={"ability_ids"})
    for field, value in update_data.items():
        setattr(character, field, value)
    # Обновляем способности, если переданы
    if data.ability_ids is not None:
        res = await db.execute(
            select(AbilityModel).where(AbilityModel.id.in_(data.ability_ids))
        )
        character.abilities = res.scalars().all()
    await db.commit()
    await db.refresh(character)
    return character

@router.delete("/{character_id}", status_code=204)
async def delete_character(character_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удалить персонажа по ID.
    """
    result = await db.execute(
        select(CharacterModel).where(CharacterModel.id == character_id)
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    await db.delete(character)
    await db.commit()

@router.get("/{character_id}/inventory", response_model=List[InventoryRead])
async def character_inventory(character_id: int, db: AsyncSession = Depends(get_db)):
    """
    Вернуть список предметов в инвентаре данного персонажа.
    """
    # Проверяем существование персонажа
    res_char = await db.execute(
        select(CharacterModel).where(CharacterModel.id == character_id)
    )
    char = res_char.scalar_one_or_none()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")

    # Загружаем инвентарь для персонажа
    res_inv = await db.execute(
        select(InventoryModel).where(InventoryModel.character_id == character_id)
    )
    return res_inv.scalars().all()