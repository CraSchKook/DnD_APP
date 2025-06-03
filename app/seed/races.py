# app/seed/races.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.race import Race

async def seed_races(db: AsyncSession):
    races = [
        {"name": "Human", "strength_bonus": 1, "dexterity_bonus": 1, "constitution_bonus": 1,
         "intelligence_bonus": 1, "wisdom_bonus": 1, "charisma_bonus": 1},
        {"name": "Elf", "strength_bonus": 0, "dexterity_bonus": 2, "constitution_bonus": 0,
         "intelligence_bonus": 1, "wisdom_bonus": 0, "charisma_bonus": 0},
        {"name": "Orc", "strength_bonus": 2, "dexterity_bonus": 0, "constitution_bonus": 1,
         "intelligence_bonus": -1, "wisdom_bonus": 0, "charisma_bonus": -1},
    ]
    for race in races:
        exists = await db.execute(select(Race).where(Race.name == race["name"]))
        if not exists.scalar_one_or_none():
            db.add(Race(**race))
    await db.commit()
