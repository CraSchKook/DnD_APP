from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.database import get_db
from app.models.effect import Effect as EffectModel
from app.schemas.effect import EffectCreate, EffectRead, EffectUpdate

router = APIRouter(prefix="/effects", tags=["Effects"])

@router.get("/", response_model=List[EffectRead])
async def list_effects(db: AsyncSession = Depends(get_db)):
    """Вернуть все эффекты."""
    result = await db.execute(select(EffectModel))
    return result.scalars().all()

@router.get("/character/{character_id}", response_model=List[EffectRead])
async def list_character_effects(
    character_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Вернуть все эффекты, действующие на конкретного персонажа."""
    result = await db.execute(
        select(EffectModel)
        .where(
            (EffectModel.target_type == "character") &
            (EffectModel.target_id == character_id)
        )
    )
    return result.scalars().all()

@router.get("/session/{session_id}", response_model=List[EffectRead])
async def list_session_effects(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Вернуть все эффекты, действующие на конкретной сессии."""
    result = await db.execute(
        select(EffectModel)
        .where(
            (EffectModel.target_type == "session") &
            (EffectModel.target_id == session_id)
        )
    )
    return result.scalars().all()

@router.post("/", response_model=EffectRead, status_code=201)
async def create_effect(data: EffectCreate, db: AsyncSession = Depends(get_db)):
    """Создать новый эффект."""
    effect = EffectModel(**data.dict())
    db.add(effect)
    await db.commit()
    await db.refresh(effect)
    return effect

@router.put("/{effect_id}", response_model=EffectRead)
async def update_effect(
    effect_id: int,
    data: EffectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить существующий эффект."""
    result = await db.execute(select(EffectModel).where(EffectModel.id == effect_id))
    effect = result.scalar_one_or_none()
    if not effect:
        raise HTTPException(status_code=404, detail="Effect not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(effect, field, value)
    await db.commit()
    await db.refresh(effect)
    return effect

@router.delete("/{effect_id}", status_code=204)
async def delete_effect(effect_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить эффект по ID."""
    result = await db.execute(select(EffectModel).where(EffectModel.id == effect_id))
    effect = result.scalar_one_or_none()
    if not effect:
        raise HTTPException(status_code=404, detail="Effect not found")
    await db.delete(effect)
    await db.commit()
    return