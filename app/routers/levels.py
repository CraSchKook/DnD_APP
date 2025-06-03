from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.level import Level as LevelModel
from app.schemas.level import LevelCreate, LevelRead

router = APIRouter(
    prefix="/levels",
    tags=["Levels"]
)

@router.get("/", response_model=List[LevelRead])
async def list_levels(db: AsyncSession = Depends(get_db)):
    """
    Вернуть список всех уровней (1, 2, …) с их бонусами.
    """
    result = await db.execute(select(LevelModel))
    levels = result.scalars().all()
    return levels

@router.get("/{level_id}", response_model=LevelRead)
async def get_level(level_id: int, db: AsyncSession = Depends(get_db)):
    """
    Вернуть конкретный уровень по его ID.
    """
    result = await db.execute(select(LevelModel).where(LevelModel.id == level_id))
    lvl = result.scalar_one_or_none()
    if not lvl:
        raise HTTPException(status_code=404, detail="Level not found")
    return lvl

@router.post("/", response_model=LevelRead, status_code=201)
async def create_level(lvl: LevelCreate, db: AsyncSession = Depends(get_db)):
    """
    Добавить новый уровень (для тестов/seed).
    """
    new_lvl = LevelModel(
        id=lvl.id,
        hp_increase=lvl.hp_increase,
        bonus_attribute=lvl.bonus_attribute,
        description=lvl.description
    )
    db.add(new_lvl)
    await db.commit()
    await db.refresh(new_lvl)
    return new_lvl
