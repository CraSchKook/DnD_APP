# app/seed/abilities.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.ability import Ability
from app.models.race import Race
from app.models.profession import Profession

async def seed_abilities(db: AsyncSession):
    """
    Создаёт 12 базовых способностей (Ability) и сразу устанавливает:
    - связи к Race (какие расы могут выбрать эту способность),
    - связи к Profession (какие классы её получают/могут выбрать).
    """
    # Определяем список всех способностей и их «правила доступа»
    ability_seeds = [
        {
            "name": "Rage",
            "description": "Barbarian enters a furious rage, получая бонусы к оружейным атакам и сопротивлению урону.",
            "cooldown": 0.0,
            "activation_condition": {},
            "allowed_race_names": [],  # доступно всем расам
            "allowed_profession_names": ["Barbarian"]
        },
        {
            "name": "Sneak Attack",
            "description": "Rogue наносит дополнительный урон, когда атакует с преимуществом или союзник рядом.",
            "cooldown": 0.0,
            "activation_condition": {},
            "allowed_race_names": [],
            "allowed_profession_names": ["Rogue"]
        },
        {
            "name": "Spellcasting",
            "description": "Permits casting class spells (Wizard/Cleric/Druid/Bard/Warlock/Sorcerer).",
            "cooldown": 0.0,
            "activation_condition": {},
            "allowed_race_names": [],
            "allowed_profession_names": ["Wizard", "Cleric", "Druid", "Bard", "Warlock", "Sorcerer"]
        },
        {
            "name": "Action Surge",
            "description": "Fighter получает дополнительное действие один раз за короткий отдых.",
            "cooldown": 0.0,
            "activation_condition": {},
            "allowed_race_names": [],
            "allowed_profession_names": ["Fighter"]
        },
        {
            "name": "Divine Smite",
            "description": "Paladin тратит ячейку заклинания, чтобы нанести дополнительный святой урон.",
            "cooldown": 0.0,
            "activation_condition": {},
            "allowed_race_names": [],
            "allowed_profession_names": ["Paladin"]
        },
        {
            "name": "Channel Divinity",
            "description": "Cleric получает особую способность, зависящую от выбранного Домена.",
            "cooldown": 0.0,
            "activation_condition": {},
            "allowed_race_names": [],
            "allowed_profession_names": ["Cleric"]
        },
        {
            "name": "Wild Shape",
            "description": "Druid может превращаться в животное дважды в короткий отдых.",
            "cooldown": 0.0,
            "activation_condition": {},
            "allowed_race_names": [],
            "allowed_profession_names": ["Druid"]
        },
        {
            "name": "Bardic Inspiration",
            "description": "Bard дает союзнику кубик вдохновения для бросков искушений или сохранений.",
            "cooldown": 0.0,
            "activation_condition": {},
            "allowed_race_names": [],
            "allowed_profession_names": ["Bard"]
        },
        {
            "name": "Evasion",
            "description": "Rogue или Monk получает половину урона от эффектов, требующих спасбросок Ловкости.",
            "cooldown": 0.0,
            "activation_condition": {},
            "allowed_race_names": [],
            "allowed_profession_names": ["Rogue", "Monk"]
        },
        {
            "name": "Ki Strike",
            "description": "Monk наносит дополнительные удары ки, повышая урон.",
            "cooldown": 0.0,
            "activation_condition": {},
            "allowed_race_names": [],
            "allowed_profession_names": ["Monk"]
        },
        {
            "name": "Second Wind",
            "description": "Fighter восстанавливает немного HP как бонусное действие.",
            "cooldown": 0.0,
            "activation_condition": {},
            "allowed_race_names": [],
            "allowed_profession_names": ["Fighter"]
        },
        {
            "name": "Arcane Recovery",
            "description": "Wizard восстанавливает часть ячеек заклинаний при коротком отдыхе.",
            "cooldown": 0.0,
            "activation_condition": {},
            "allowed_race_names": [],
            "allowed_profession_names": ["Wizard"]
        },
        {
            "name": "УДАР ДУРАКА",
            "description": "ЕСЛИ ТЫ ДУРАК - УДАРЬ КАК ДУРАК",
            "cooldown": 0.0,
            "activation_condition": {},
            "allowed_race_names": ["Orc", "Gnome"],
            "allowed_profession_names": [] # доступно всем классам
        },
        {
            "name": "Взрыв энергии",
            "description": "Создаёт мощную волну, наносящую урон всем вокруг.",
            "cooldown": 60.0,
            "activation_condition": {"requires_shards": {"red": 1}, "uses_per_long_rest": 2},
            "allowed_race_names": [],            # ← ОБЯЗАТЕЛЬНО
            "allowed_profession_names": []       # ← ОБЯЗАТЕЛЬНО
        },
        {
            "name": "Усиленная регенерация",
            "description": "Увеличивает восстановление HP вдвое на 1 минуту.",
            "cooldown": 120.0,
            "activation_condition": {"requires_shards": {"green": 1}, "uses_per_long_rest": 1},
            "allowed_race_names": [],
            "allowed_profession_names": []
        },
        {
            "name": "Ускорение времени",
            "description": "Действия персонажа ускоряются на 10 секунд.",
            "cooldown": 90.0,
            "activation_condition": {"requires_shards": {"blue": 1}, "uses_per_long_rest": 2},
            "allowed_race_names": [],
            "allowed_profession_names": []
        },
        {
            "name": "Теневой скачок",
            "description": "Телепорт на 15 метров.",
            "cooldown": 45.0,
            "activation_condition": {"requires_shards": {"black": 1}, "uses_per_long_rest": 2, "range_meters": 15},
            "allowed_race_names": [],
            "allowed_profession_names": []
        },
        {
            "name": "Призыв чистоты",
            "description": "Очистка всех негативных эффектов и восстановление 5 HP.",
            "cooldown": 300.0,
            "activation_condition": {"requires_shards": {"white": 1}, "uses_per_long_rest": 1},
            "allowed_race_names": [],
            "allowed_profession_names": []
        },
    ]

    for a in ability_seeds:
        # Проверяем, есть ли уже Ability с таким именем
        stmt = await db.execute(select(Ability).where(Ability.name == a["name"]))
        existing = stmt.scalar_one_or_none()
        if existing:
            continue

        # Если нет — создаём новую Ability
        ability = Ability(
            name=a["name"],
            description=a["description"],
            cooldown=a["cooldown"],
            activation_condition=a.get("activation_condition")
        )

        # Связываем с расами (если указаны по имени)
        if a["allowed_race_names"]:
            stmt_r = await db.execute(
                select(Race).where(Race.name.in_(a["allowed_race_names"]))
            )
            ability.races = stmt_r.scalars().all()

        # Связываем с профессиями (если указаны по имени)
        if a["allowed_profession_names"]:
            stmt_p = await db.execute(
                select(Profession).where(Profession.name.in_(a["allowed_profession_names"]))
            )
            ability.professions = stmt_p.scalars().all()

        db.add(ability)

    await db.commit()
