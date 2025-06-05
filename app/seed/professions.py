from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.profession import Profession

async def seed_professions(db: AsyncSession):
    """
    Канонические классы (профессии) и их бонусы (D&D 5e).
    Выполняет INSERT только если профессия с таким именем ещё не существует.
    """
    professions = [
        {"name": "Barbarian", "hit_die": 12, "strength_bonus": 2, "dexterity_bonus": 0, "constitution_bonus": 2, "intelligence_bonus": 0, "wisdom_bonus": 0, "charisma_bonus": 0},
        {"name": "Bard",      "hit_die": 8,  "strength_bonus": 0, "dexterity_bonus": 0, "constitution_bonus": 0, "intelligence_bonus": 0, "wisdom_bonus": 0, "charisma_bonus": 2},
        {"name": "Cleric",    "hit_die": 8,  "strength_bonus": 0, "dexterity_bonus": 0, "constitution_bonus": 0, "intelligence_bonus": 0, "wisdom_bonus": 2, "charisma_bonus": 0},
        {"name": "Druid",     "hit_die": 8,  "strength_bonus": 0, "dexterity_bonus": 0, "constitution_bonus": 0, "intelligence_bonus": 0, "wisdom_bonus": 2, "charisma_bonus": 0},
        {"name": "Fighter",   "hit_die": 10, "strength_bonus": 0, "dexterity_bonus": 0, "constitution_bonus": 0, "intelligence_bonus": 0, "wisdom_bonus": 0, "charisma_bonus": 0},
        {"name": "Monk",      "hit_die": 8,  "strength_bonus": 0, "dexterity_bonus": 2, "constitution_bonus": 0, "intelligence_bonus": 0, "wisdom_bonus": 1, "charisma_bonus": 0},
        {"name": "Paladin",   "hit_die": 10, "strength_bonus": 0, "dexterity_bonus": 0, "constitution_bonus": 0, "intelligence_bonus": 0, "wisdom_bonus": 0, "charisma_bonus": 1},
        {"name": "Ranger",    "hit_die": 10, "strength_bonus": 0, "dexterity_bonus": 1, "constitution_bonus": 0, "intelligence_bonus": 0, "wisdom_bonus": 1, "charisma_bonus": 0},
        {"name": "Rogue",     "hit_die": 8,  "strength_bonus": 0, "dexterity_bonus": 2, "constitution_bonus": 0, "intelligence_bonus": 1, "wisdom_bonus": 0, "charisma_bonus": 0},
        {"name": "Sorcerer",  "hit_die": 6,  "strength_bonus": 0, "dexterity_bonus": 0, "constitution_bonus": 0, "intelligence_bonus": 0, "wisdom_bonus": 0, "charisma_bonus": 2},
        {"name": "Warlock",   "hit_die": 8,  "strength_bonus": 0, "dexterity_bonus": 0, "constitution_bonus": 0, "intelligence_bonus": 0, "wisdom_bonus": 0, "charisma_bonus": 2},
        {"name": "Wizard",    "hit_die": 6,  "strength_bonus": 0, "dexterity_bonus": 0, "constitution_bonus": 0, "intelligence_bonus": 2, "wisdom_bonus": 0, "charisma_bonus": 0},
    ]

    for prof_data in professions:
        stmt = await db.execute(select(Profession).where(Profession.name == prof_data["name"]))
        existing = stmt.scalar_one_or_none()
        if not existing:
            db.add(Profession(**prof_data))

    await db.commit()
