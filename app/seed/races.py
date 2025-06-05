from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.race import Race

async def seed_races(db: AsyncSession):
    """
    Канонические расы и их бонусы (D&D 5e).
    Выполняет INSERT только если раса с таким именем ещё не существует.
    """
    races = [
        {"name": "Human",           "strength_bonus": 1, "dexterity_bonus": 1, "constitution_bonus": 1, "intelligence_bonus": 1, "wisdom_bonus": 1, "charisma_bonus": 1},
        {"name": "Elf",             "strength_bonus": 0, "dexterity_bonus": 2, "constitution_bonus": 0, "intelligence_bonus": 1, "wisdom_bonus": 0, "charisma_bonus": 0},
        {"name": "High Elf",        "strength_bonus": 0, "dexterity_bonus": 2, "constitution_bonus": 0, "intelligence_bonus": 1, "wisdom_bonus": 0, "charisma_bonus": 0},
        {"name": "Dwarf",           "strength_bonus": 0, "dexterity_bonus": 0, "constitution_bonus": 2, "intelligence_bonus": 0, "wisdom_bonus": 1, "charisma_bonus": 0},
        {"name": "Hill Dwarf",      "strength_bonus": 0, "dexterity_bonus": 0, "constitution_bonus": 2, "intelligence_bonus": 0, "wisdom_bonus": 1, "charisma_bonus": 0},
        {"name": "Mountain Dwarf",  "strength_bonus": 2, "dexterity_bonus": 0, "constitution_bonus": 2, "intelligence_bonus": 0, "wisdom_bonus": 0, "charisma_bonus": 0},
        {"name": "Halfling",        "strength_bonus": 0, "dexterity_bonus": 2, "constitution_bonus": 0, "intelligence_bonus": 0, "wisdom_bonus": 0, "charisma_bonus": 1},
        {"name": "Gnome",           "strength_bonus": 0, "dexterity_bonus": 0, "constitution_bonus": 0, "intelligence_bonus": 2, "wisdom_bonus": 0, "charisma_bonus": 0},
        {"name": "Half-Elf",        "strength_bonus": 0, "dexterity_bonus": 0, "constitution_bonus": 0, "intelligence_bonus": 0, "wisdom_bonus": 0, "charisma_bonus": 2},
        {"name": "Half-Orc",        "strength_bonus": 2, "dexterity_bonus": 0, "constitution_bonus": 1, "intelligence_bonus": 0, "wisdom_bonus": 0, "charisma_bonus": 0},
        {"name": "Tiefling",        "strength_bonus": 0, "dexterity_bonus": 0, "constitution_bonus": 0, "intelligence_bonus": 1, "wisdom_bonus": 0, "charisma_bonus": 2},
        {"name": "Dragonborn",      "strength_bonus": 2, "dexterity_bonus": 0, "constitution_bonus": 0, "intelligence_bonus": 0, "wisdom_bonus": 0, "charisma_bonus": 1},
        {"name": "Orc",             "strength_bonus": 2, "dexterity_bonus": 1, "constitution_bonus": 1, "intelligence_bonus": 0, "wisdom_bonus": 0, "charisma_bonus": 0},
    ]

    for race_data in races:
        stmt = await db.execute(select(Race).where(Race.name == race_data["name"]))
        existing = stmt.scalar_one_or_none()
        if not existing:
            db.add(Race(**race_data))

    await db.commit()
