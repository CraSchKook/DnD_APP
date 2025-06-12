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

    strength_user: int = Field(..., description="Показатель Силы")
    dexterity_user: int = Field(..., description="Показатель Ловкости")
    constitution_user: int = Field(..., description="Показатель Телосложения")
    intelligence_user: int = Field(..., description="Показатель Интеллекта")
    wisdom_user: int = Field(..., description="Показатель Мудрости")
    charisma_user: int = Field(..., description="Показатель Харизмы")

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

    strength_user: Optional[int] = Field(None, description="Показатель Силы")
    dexterity_user: Optional[int] = Field(None, description="Показатель Ловкости")
    constitution_user: Optional[int] = Field(None, description="Показатель Телосложения")
    intelligence_user: Optional[int] = Field(None, description="Показатель Интеллекта")
    wisdom_user: Optional[int] = Field(None, description="Показатель Мудрости")
    charisma_user: Optional[int] = Field(None, description="Показатель Харизмы")

    race_id: Optional[int] = Field(None, description="ID расы (из списка /races)")
    profession_id: Optional[int] = Field(None, description="ID класса (из списка /professions)")
    level_id: Optional[int] = Field(None, description="ID уровня (из списка /levels)")

    ability_ids: Optional[List[int]] = None
    is_npc: Optional[bool] = Field(default=None, description="Является ли NPC")
    avatar_url: Optional[str] = Field(None, description="URL аватара персонажа")

    shards: Optional[Dict[str, int]] = Field(
        None,
        description="Осколки всех пяти цветов"
    ) # осколки - универсальная механика и основа лора.

class CharacterRead(BaseModel):
    id: int = Field(..., description="ID персонажа")
    name: str
    player_id: Optional[int]
    session_id: Optional[int]

    race: RaceRead
    profession: ProfessionRead
    level: LevelRead

    hp: int
    armor: int
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    shards: Dict[str, int]

    is_npc: bool
    avatar_url: Optional[str] = None

    abilities: List[AbilityRead] = Field(default_factory=list)
    inventory_items: List[InventoryItemRead] = Field(default_factory=list)

    class Config:
        orm_mode = True
        model_config = {"from_attributes": True}
