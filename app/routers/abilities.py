from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.ability import Ability as AbilityModel
from app.schemas.ability import AbilityCreate, AbilityRead, AbilityUpdate

router = APIRouter(prefix="/abilities", tags=["Abilities"])

@router.get("/", response_model=list[AbilityRead])
async def list_abilities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AbilityModel)
        .options(selectinload(AbilityModel.character))
    )
    return result.scalars().all()

@router.get("/{ability_id}", response_model=AbilityRead)
async def read_ability(ability_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AbilityModel).where(AbilityModel.id == ability_id))
    ability = result.scalar_one_or_none()
    if not ability:
        raise HTTPException(404, "Ability not found")
    return ability

@router.post("/", response_model=AbilityRead, status_code=201)
async def create_ability(data: AbilityCreate, db: AsyncSession = Depends(get_db)):
    ability = AbilityModel(**data.dict())
    db.add(ability)
    await db.commit()
    await db.refresh(ability)
    return ability

@router.put("/{ability_id}", response_model=AbilityRead)
async def update_ability(ability_id: int, data: AbilityUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AbilityModel).where(AbilityModel.id == ability_id))
    ability = result.scalar_one_or_none()
    if not ability:
        raise HTTPException(404, "Ability not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(ability, field, value)
    await db.commit()
    await db.refresh(ability)
    return ability

@router.delete("/{ability_id}", status_code=204)
async def delete_ability(ability_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AbilityModel).where(AbilityModel.id == ability_id))
    ability = result.scalar_one_or_none()
    if not ability:
        raise HTTPException(404, "Ability not found")
    await db.delete(ability)
    await db.commit()