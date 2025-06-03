from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.profession import Profession as ProfessionModel
from app.schemas.profession import ProfessionCreate, ProfessionRead

router = APIRouter(
    prefix="/professions",
    tags=["professions"]
)

@router.get("/", response_model=List[ProfessionRead])
async def list_professions(db: AsyncSession = Depends(get_db)):
    """
    Вернуть список всех классов (Fighter, Rogue, …) и их базовые бонусы.
    """
    result = await db.execute(select(ProfessionModel))
    professions = result.scalars().all()
    return professions

@router.get("/{Profession_id}", response_model=ProfessionRead)
async def get_Profession(Profession_id: int, db: AsyncSession = Depends(get_db)):
    """
    Вернуть детали конкретного класса по его ID.
    """
    result = await db.execute(select(ProfessionModel).where(ProfessionModel.id == Profession_id))
    cls = result.scalar_one_or_none()
    if not cls:
        raise HTTPException(status_code=404, detail="professions not found")
    return cls

@router.post("/", response_model=ProfessionRead, status_code=201)
async def create_Profession(cls: ProfessionCreate, db: AsyncSession = Depends(get_db)):
    """
    Добавить новый класс (для тестов/seed).
    """
    new_cls = ProfessionModel(
        name=cls.name,
        hit_die=cls.hit_die,
        strength_bonus=cls.strength_bonus,
        dexterity_bonus=cls.dexterity_bonus,
        constitution_bonus=cls.constitution_bonus,
        intelligence_bonus=cls.intelligence_bonus,
        wisdom_bonus=cls.wisdom_bonus,
        charisma_bonus=cls.charisma_bonus,
    )
    db.add(new_cls)
    await db.commit()
    await db.refresh(new_cls)
    return new_cls
