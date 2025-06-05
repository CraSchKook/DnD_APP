from typing import Dict
from app.models.race import Race
from app.models.profession import Profession
from app.models.level import Level

def compute_final_stats(
    race: Race,
    cls: Profession,
    lvl: Level,
    strength_user: int,
    dexterity_user: int,
    constitution_user: int,
    intelligence_user: int,
    wisdom_user: int,
    charisma_user: int
) -> Dict[str, int]:
    """
    Рассчитывает финальные статы персонажа с учётом:
    1. «Сырого» ввода игрока (strength_user, dexterity_user и т.д.).
    2. Бонусов/штрафов расы (race.*_bonus).
    3. Бонусов/штрафов класса (cls.*_bonus).
    4. Базового HP на 1-м уровне (hit_die) + расовый бонус (race.extra_hp * lvl.id) + модификатор CON.
    5. AC (Armor Class) = 8 + модификатор DEX.
    """

    # 1. Начальные «сырые» статы (до бонусов расы/класса)
    base = {
        "strength": strength_user,
        "dexterity": dexterity_user,
        "constitution": constitution_user,
        "intelligence": intelligence_user,
        "wisdom": wisdom_user,
        "charisma": charisma_user,
    }

    # 2. Применяем бонусы/штрафы расы к базовым статам
    base["strength"]     += race.strength_bonus
    base["dexterity"]    += race.dexterity_bonus
    base["constitution"] += race.constitution_bonus
    base["intelligence"] += race.intelligence_bonus
    base["wisdom"]       += race.wisdom_bonus
    base["charisma"]     += race.charisma_bonus

    # 3. Применяем бонусы/штрафы класса (профессии) к базовым статам
    base["strength"]     += cls.strength_bonus
    base["dexterity"]    += cls.dexterity_bonus
    base["constitution"] += cls.constitution_bonus
    base["intelligence"] += cls.intelligence_bonus
    base["wisdom"]       += cls.wisdom_bonus
    base["charisma"]     += cls.charisma_bonus

    # 4. Вычисляем модификаторы: (stat - 10) // 2
    def ability_modifier(stat_value: int) -> int:
        return (stat_value - 10) // 2

    mods = {stat: ability_modifier(val) for stat, val in base.items()}

    # 5. Рассчитываем HP:
    #    hit_die (например, 8) + модификатор CON + (lvl.id * race.extra_hp)
    #    lvl.id — номер уровня (1, 2, 3 и т.д.), race.extra_hp — бонус HP от расы на каждый уровень
    hp_total = cls.hit_die + mods["constitution"] + lvl.id * race.extra_hp

    # 6. Рассчитываем Armor Class (AC):
    #    Базовая формула: 8 + модификатор DEX
    armor = 8 + mods["dexterity"]

    # 7. Если lvl.bonus_attribute указан, повышаем соответствующий атрибут на +1 (не влияет на HP здесь)
    if lvl.bonus_attribute:
        stat_name = lvl.bonus_attribute.lower()
        if stat_name in base:
            base[stat_name] += 1
            mods[stat_name] = ability_modifier(base[stat_name])

    # 8. Составляем итоговый словарь с финальными статами
    final = {
        "hp": hp_total,
        "armor": armor,
        "strength": base["strength"],
        "dexterity": base["dexterity"],
        "constitution": base["constitution"],
        "intelligence": base["intelligence"],
        "wisdom": base["wisdom"],
        "charisma": base["charisma"],
    }
    return final
