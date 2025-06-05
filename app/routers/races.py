from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.race import Race as RaceModel
from app.schemas.race import RaceCreate, RaceRead

router = APIRouter(
    prefix="/races",
    tags=["Races"]
)

@router.get("/", response_model=List[RaceRead])
async def list_races(db: AsyncSession = Depends(get_db)):
    """
    Вернуть список всех рас с их бонусами, штрафами и расширенными полями.
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
    Добавить новую расу с расширенными параметрами.
    """
    new_race = RaceModel(
        name=race.name,
        strength_bonus=race.strength_bonus,
        dexterity_bonus=race.dexterity_bonus,
        constitution_bonus=race.constitution_bonus,
        intelligence_bonus=race.intelligence_bonus,
        wisdom_bonus=race.wisdom_bonus,
        charisma_bonus=race.charisma_bonus,

        # Новые поля:
        extra_hp=race.extra_hp,
        movement_speed=race.movement_speed,
        night_vision=race.night_vision,
        resistances=race.resistances,
        languages=race.languages,
        traits=race.traits,
    )
    db.add(new_race)
    await db.commit()
    await db.refresh(new_race)
    return new_race