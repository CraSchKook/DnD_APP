from pydantic import BaseModel, Field
from typing import Optional, List, Dict

from app.schemas.ability import AbilityRead
from app.schemas.race import RaceRead
from app.schemas.profession import ProfessionRead
from app.schemas.level import LevelRead
from app.schemas.inventory import InventoryItemRead

class CharacterBase(BaseModel):
    name: str = Field(..., description="Имя персонажа")

    # ← «финальные» статы, которые присылает фронтенд
    hp: int = Field(..., description="Итоговое значение ХП после всех бонусов")
    armor: int = Field(..., description="Итоговое значение Класса Брони после всех бонусов")

    strength: int = Field(..., description="Показатель Силы")
    dexterity: int = Field(..., description="Показатель Ловкости")
    constitution: int = Field(..., description="Показатель Телосложения")
    intelligence: int = Field(..., description="Показатель Интеллекта")
    wisdom: int = Field(..., description="Показатель Мудрости")
    charisma: int = Field(..., description="Показатель Харизмы")

    race_id: int = Field(..., description="ID расы (из списка /races)")
    profession_id: int = Field(..., description="ID профессии/класса (из списка /professions)")
    level_id: int = Field(..., description="ID уровня (из списка /levels)")

    is_npc: bool = Field(default=False, description="Является ли NPC")
    avatar_url: Optional[str] = Field(None, description="URL аватара персонажа")

    shards: Dict[str, int] = Field(
        default_factory=lambda: {
            "red": 0,
            "green": 0,
            "blue": 0,
            "black": 0,
            "white": 0
        },
        description="Осколки пяти"
    )

class CharacterCreate(CharacterBase):
    ability_ids: Optional[List[int]] = Field(
        default_factory=list,
        description="Список ID способностей для присвоения"
    )
    session_id: Optional[int] = Field(None, description="ID сессии, если персонаж участвует")

class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Новое имя персонажа")
    session_id: Optional[int] = Field(None, description="Обновлённый ID сессии")

    hp: Optional[int] = Field(None, description="Итоговое значение ХП после всех бонусов")
    armor: Optional[int] = Field(None, description="Итоговое значение Класса Брони после всех бонусов")

    strength: Optional[int] = Field(None, description="Показатель Силы")
    dexterity: Optional[int] = Field(None, description="Показатель Ловкости")
    constitution: Optional[int] = Field(None, description="Показатель Телосложения")
    intelligence: Optional[int] = Field(None, description="Показатель Интеллекта")
    wisdom: Optional[int] = Field(None, description="Показатель Мудрости")
    charisma: Optional[int] = Field(None, description="Показатель Харизмы")

    race_id: Optional[int] = Field(None, description="ID расы (из списка /races)")
    profession_id: Optional[int] = Field(None, description="ID класса (из списка /professions)")
    level_id: Optional[int] = Field(None, description="ID уровня (из списка /levels)")

    ability_ids: Optional[List[int]] = Field(
        None,
        alias="abilities",
        description="Список ID способностей",
    )
    is_npc: Optional[bool] = Field(None, description="Является ли NPC")
    avatar_url: Optional[str] = Field(None, description="URL аватара персонажа")

    shards: Optional[Dict[str, int]] = Field(
        None,
        description="Осколки всех пяти цветов"
    ) # осколки - универсальная механика и основа лора.

class CharacterRead(BaseModel):
    id: int = Field(..., description="ID персонажа")
    name: str = Field(..., description="Имя персонажа")
    player_id: Optional[int] = Field(None, description="ID владельца персонажа (игрока)")
    session_id: Optional[int] = Field(None, description="ID сессии, в которой участвует персонаж")

    race: RaceRead = Field(..., description="Данные расы персонажа")
    profession: ProfessionRead = Field(..., description="Данные профессии (класса) персонажа")
    level: LevelRead = Field(..., description="Данные уровня персонажа")

    hp: int = Field(..., description="Финальное значение ХП")
    armor: int = Field(..., description="Финальное значение AC (класса брони)")
    shards: Dict[str, int] = Field(..., description="Количество осколков по цветам")
    
    strength: int = Field(..., description="Финальное значение Силы")
    dexterity: int = Field(..., description="Финальное значение Ловкости")
    constitution: int = Field(..., description="Финальное значение Телосложения")
    intelligence: int = Field(..., description="Финальное значение Интеллекта")
    wisdom: int = Field(..., description="Финальное значение Мудрости")
    charisma: int = Field(..., description="Финальное значение Харизмы")

    is_npc: bool = Field(..., description="Флаг: является ли персонаж NPC")
    avatar_url: Optional[str] = Field(None, description="URL аватара персонажа (если задан)")

    abilities: List[AbilityRead] = Field(default_factory=list, description="Список способностей персонажа")
    inventory_items: List[InventoryItemRead] = Field(default_factory=list, description="Инвентарь персонажа")

    class Config:
        orm_mode = True
        model_config = {"from_attributes": True}
