# app/seed/levels.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.level import Level

async def seed_levels(db: AsyncSession):
    for lvl in range(1, 21): # D&D обычно от 1 до 20 уровня
        exists = await db.execute(select(Level).where(Level.id == lvl))
        if not exists.scalar_one_or_none():
            db.add(Level(id=lvl, hp_increase=5, bonus_attribute="None", description=""))
    await db.commit()