# app/seed/professions.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.profession import Profession

async def seed_professions(db: AsyncSession):
    professions = [
        {"name": "Fighter", "hit_die": 10},  # d10 для Fighter
        {"name": "Wizard", "hit_die": 6},    # d6 для Wizard
        {"name": "Rogue", "hit_die": 8},     # d8 для Rogue
    ]
    for prof in professions:
        exists = await db.execute(select(Profession).where(Profession.name == prof["name"]))
        if not exists.scalar_one_or_none():
            db.add(Profession(**prof))
    await db.commit()
