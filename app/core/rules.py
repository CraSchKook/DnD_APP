# app/core/rules.py
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
    Рассчитывает финальные статы персонажа, комбинируя:
    • «сырые» пользовательские 6 характеристик (strength_user, …).
    • бонусы или штрафы расы (race.*_bonus).
    • бонусы или штрафы класса (cls.*_bonus).
    • бонусы уровня: lvl.hp_increase, lvl.bonus_attribute.
    • базовые HP (hit_die у класса) и AC (например, 10 + модификатор dexterity).
    """

    # 1. Начальные «сырые» статы
    base = {
        "strength": strength_user,
        "dexterity": dexterity_user,
        "constitution": constitution_user,
        "intelligence": intelligence_user,
        "wisdom": wisdom_user,
        "charisma": charisma_user,
    }

    # 2. Применяем бонусы/штрафы расы
    base["strength"] += race.strength_bonus
    base["dexterity"] += race.dexterity_bonus
    base["constitution"] += race.constitution_bonus
    base["intelligence"] += race.intelligence_bonus
    base["wisdom"] += race.wisdom_bonus
    base["charisma"] += race.charisma_bonus

    # 3. Применяем бонусы/штрафы класса
    base["strength"] += cls.strength_bonus
    base["dexterity"] += cls.dexterity_bonus
    base["constitution"] += cls.constitution_bonus
    base["intelligence"] += cls.intelligence_bonus
    base["wisdom"] += cls.wisdom_bonus
    base["charisma"] += cls.charisma_bonus

    # 4. Модификаторы: обычно (stat - 10) // 2
    #    Например, если strength = 14, мод = +2; если 9 → -1
    def ability_modifier(stat_value: int) -> int:
        return (stat_value - 10) // 2

    mods = {stat: ability_modifier(val) for stat, val in base.items()}

    # 5. Рассчитываем HP:
    #    Обычно: на 1 уровне HP = hit_die (например, Fighter=10) + модификатор конституции
    #             + бонус уровня (lvl.hp_increase) * (level - 1)  (если вы хотите масштаб)
    #    Для простоты сделаем: 
    #       hp = cls.hit_die + mods["constitution"] + lvl.hp_increase
    #
    hp = cls.hit_die + mods["constitution"] + lvl.hp_increase

    # 6. Рассчитываем Armor (AC):
    #    Классическая формула: 10 + модификатор dexterity
    armor = 10 + mods["dexterity"]

    # 7. Если lvl.bonus_attribute указан, поднять этот атрибут ещё на +1:
    if lvl.bonus_attribute:
        stat_name = lvl.bonus_attribute.lower()  # ожидаем, что это допустимый ключ, например, "strength"
        if stat_name in base:
            base[stat_name] += 1
            mods[stat_name] = ability_modifier(base[stat_name])
            # Можно учитывать это в HP (если это constitution), но для простоты оставим как есть.

    # 8. Финальный словарь:
    final = {
        "hp": hp,
        "armor": armor,
        "strength": base["strength"],
        "dexterity": base["dexterity"],
        "constitution": base["constitution"],
        "intelligence": base["intelligence"],
        "wisdom": base["wisdom"],
        "charisma": base["charisma"],
    }
    return final
