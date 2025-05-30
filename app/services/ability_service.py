# app/services/ability_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.models.ability import Ability as AbilityModel
from app.models.character import Character as CharacterModel
from app.models.npc import NPC as NPCModel
from app.schemas.ability import AbilityCreate, AbilityUpdate

async def list_abilities(db: AsyncSession):
    result = await db.execute(
        select(AbilityModel)
        .options(
            # optionally load related characters and npcs
            # selectinload(AbilityModel.characters),
            # selectinload(AbilityModel.npcs)
        )
    )
    return result.scalars().all()

async def get_ability(ability_id: int, db: AsyncSession):
    result = await db.execute(select(AbilityModel).where(AbilityModel.id == ability_id))
    ability = result.scalar_one_or_none()
    if not ability:
        raise HTTPException(404, "Ability not found")
    return ability

async def create_ability(data: AbilityCreate, db: AsyncSession):
    ability = AbilityModel(
        name=data.name,
        description=data.description or "",
        cooldown=data.cooldown
    )
    # привязка к персонажам
    if data.character_ids:
        chars = await db.execute(
            select(CharacterModel).where(CharacterModel.id.in_(data.character_ids))
        )
        ability.characters = chars.scalars().all()
    # привязка к NPC
    if data.npc_ids:
        npcs = await db.execute(
            select(NPCModel).where(NPCModel.id.in_(data.npc_ids))
        )
        ability.npcs = npcs.scalars().all()
    db.add(ability)
    await db.commit()
    await db.refresh(ability)
    return ability

async def update_ability(ability_id: int, data: AbilityUpdate, db: AsyncSession):
    ability = await get_ability(ability_id, db)
    # обновление полей
    for field, value in data.dict(exclude_unset=True, exclude={"character_ids", "npc_ids"}).items():
        setattr(ability, field, value)
    # обновление связей
    if data.character_ids is not None:
        chars = await db.execute(
            select(CharacterModel).where(CharacterModel.id.in_(data.character_ids))
        )
        ability.characters = chars.scalars().all()
    if data.npc_ids is not None:
        npcs = await db.execute(
            select(NPCModel).where(NPCModel.id.in_(data.npc_ids))
        )
        ability.npcs = npcs.scalars().all()
    await db.commit()
    await db.refresh(ability)
    return ability

async def delete_ability(ability_id: int, db: AsyncSession):
    ability = await get_ability(ability_id, db)
    await db.delete(ability)
    await db.commit()