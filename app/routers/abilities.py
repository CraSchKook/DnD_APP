from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.ability import Ability as AbilityModel
from app.models.character import Character as CharacterModel
from app.models.race import Race as RaceModel
from app.models.profession import Profession as ProfessionModel
from app.schemas.ability import AbilityCreate, AbilityRead, AbilityUpdate

router = APIRouter(prefix="/abilities", tags=["Abilities"])

@router.get("/", response_model=list[AbilityRead])
async def list_abilities(db: AsyncSession = Depends(get_db)):
    """
    Получить список всех абилок с деталями по расам, классам и персонажам.
    """
    result = await db.execute(
        select(AbilityModel).options(
            selectinload(AbilityModel.races),
            selectinload(AbilityModel.professions),
            selectinload(AbilityModel.characters)
        )
    )
    abilities = result.scalars().all()

    return [
        AbilityRead(
            id=ability.id,
            name=ability.name,
            description=ability.description,
            cooldown=ability.cooldown,
            allowed_races=[r.name for r in ability.races],
            allowed_professions=[p.name for p in ability.professions],
            character_ids=[c.id for c in ability.characters]
        )
        for ability in abilities
    ]

@router.get("/{ability_id}", response_model=AbilityRead)
async def read_ability(ability_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получить одну абилку по ID.
    """
    result = await db.execute(
        select(AbilityModel)
        .options(
            selectinload(AbilityModel.races),
            selectinload(AbilityModel.professions),
            selectinload(AbilityModel.characters)
        )
        .where(AbilityModel.id == ability_id)
    )
    ability = result.scalar_one_or_none()
    if not ability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ability not found")

    return AbilityRead(
        id=ability.id,
        name=ability.name,
        description=ability.description,
        cooldown=ability.cooldown,
        allowed_races=[r.name for r in ability.races],
        allowed_professions=[p.name for p in ability.professions],
        character_ids=[c.id for c in ability.characters]
    )

@router.post("/", response_model=AbilityRead, status_code=status.HTTP_201_CREATED)
async def create_ability(data: AbilityCreate, db: AsyncSession = Depends(get_db)):
    """
    Создать новую абилку.
    """
    ability = AbilityModel(
        name=data.name,
        description=data.description,
        cooldown=data.cooldown
    )

    # Привязка к расам
    if data.allowed_race_ids:
        races = await db.execute(select(RaceModel).where(RaceModel.id.in_(data.allowed_race_ids)))
        ability.races = races.scalars().all()

    # Привязка к профессиям
    if data.allowed_profession_ids:
        profs = await db.execute(select(ProfessionModel).where(ProfessionModel.id.in_(data.allowed_profession_ids)))
        ability.professions = profs.scalars().all()

    # Привязка к персонажам (необязательно)
    if data.character_ids:
        chars = await db.execute(select(CharacterModel).where(CharacterModel.id.in_(data.character_ids)))
        ability.characters = chars.scalars().all()

    db.add(ability)
    await db.commit()
    await db.refresh(ability)

    return AbilityRead(
        id=ability.id,
        name=ability.name,
        description=ability.description,
        cooldown=ability.cooldown,
        allowed_races=[r.name for r in ability.races],
        allowed_professions=[p.name for p in ability.professions],
        character_ids=[c.id for c in ability.characters]
    )

@router.put("/{ability_id}", response_model=AbilityRead)
async def update_ability(ability_id: int, data: AbilityUpdate, db: AsyncSession = Depends(get_db)):
    """
    Обновить абилку по ID.
    """
    result = await db.execute(
        select(AbilityModel)
        .options(
            selectinload(AbilityModel.races),
            selectinload(AbilityModel.professions),
            selectinload(AbilityModel.characters)
        )
        .where(AbilityModel.id == ability_id)
    )
    ability = result.scalar_one_or_none()
    if not ability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ability not found")

    # Обновляем поля
    if data.name is not None:
        ability.name = data.name
    if data.description is not None:
        ability.description = data.description
    if data.cooldown is not None:
        ability.cooldown = data.cooldown

    # Обновляем связи
    if data.allowed_race_ids is not None:
        races = await db.execute(select(RaceModel).where(RaceModel.id.in_(data.allowed_race_ids)))
        ability.races = races.scalars().all()

    if data.allowed_profession_ids is not None:
        profs = await db.execute(select(ProfessionModel).where(ProfessionModel.id.in_(data.allowed_profession_ids)))
        ability.professions = profs.scalars().all()

    if data.character_ids is not None:
        chars = await db.execute(select(CharacterModel).where(CharacterModel.id.in_(data.character_ids)))
        ability.characters = chars.scalars().all()

    await db.commit()
    await db.refresh(ability)

    return AbilityRead(
        id=ability.id,
        name=ability.name,
        description=ability.description,
        cooldown=ability.cooldown,
        allowed_races=[r.name for r in ability.races],
        allowed_professions=[p.name for p in ability.professions],
        character_ids=[c.id for c in ability.characters]
    )

@router.delete("/{ability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ability(ability_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удалить абилку.
    """
    result = await db.execute(select(AbilityModel).where(AbilityModel.id == ability_id))
    ability = result.scalar_one_or_none()
    if not ability:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ability not found")
    await db.delete(ability)
    await db.commit()