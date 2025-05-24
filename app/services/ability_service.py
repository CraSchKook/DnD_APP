from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.ability import Ability as AbilityModel
from app.schemas.ability import AbilityCreate, AbilityUpdate

async def list_abilities(db: AsyncSession):
    result = await db.execute(select(AbilityModel))
    return result.scalars().all()

async def get_ability(ability_id: int, db: AsyncSession):
    result = await db.execute(select(AbilityModel).where(AbilityModel.id == ability_id))
    ability = result.scalar_one_or_none()
    if not ability:
        raise HTTPException(404, "Ability not found")
    return ability

async def create_ability(data: AbilityCreate, db: AsyncSession):
    ability = AbilityModel(**data.dict())
    db.add(ability)
    await db.commit()
    await db.refresh(ability)
    return ability

async def update_ability(ability_id: int, data: AbilityUpdate, db: AsyncSession):
    ability = await get_ability(ability_id, db)
    for field, value in data.dict(exclude_unset=True).items():
        setattr(ability, field, value)
    await db.commit()
    await db.refresh(ability)
    return ability

async def delete_ability(ability_id: int, db: AsyncSession):
    ability = await get_ability(ability_id, db)
    await db.delete(ability)
    await db.commit()
