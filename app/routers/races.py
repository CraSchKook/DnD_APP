from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.race import Race as RaceModel
from app.schemas.race import RaceCreate, RaceRead

from sqlalchemy.future import select

router = APIRouter(
    prefix="/races",
    tags=["Races"]
)

@router.get("/", response_model=List[RaceRead])
async def list_races(db: AsyncSession = Depends(get_db)):
    """
    Вернуть список всех рас с их бонусами/штрафами.
    """
    result = await db.execute(select(RaceModel))
    races = result.scalars().all()
    return races

@router.get("/{race_id}", response_model=RaceRead)
async def get_race(race_id: int, db: AsyncSession = Depends(get_db)):
    """
    Вернуть детали конкретной расы по ее ID.
    """
    result = await db.execute(select(RaceModel).where(RaceModel.id == race_id))
    race = result.scalar_one_or_none()
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    return race

@router.post("/", response_model=RaceRead, status_code=201)
async def create_race(race: RaceCreate, db: AsyncSession = Depends(get_db)):
    """
    Добавить новую расу (по сути seed для тестов; на проде обычно фиксируют). 
    """
    new_race = RaceModel(
        name=race.name,
        strength_bonus=race.strength_bonus,
        dexterity_bonus=race.dexterity_bonus,
        constitution_bonus=race.constitution_bonus,
        intelligence_bonus=race.intelligence_bonus,
        wisdom_bonus=race.wisdom_bonus,
        charisma_bonus=race.charisma_bonus
    )
    db.add(new_race)
    await db.commit()
    await db.refresh(new_race)
    return new_race
