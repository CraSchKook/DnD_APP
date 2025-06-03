from pydantic import BaseModel, Field
from typing import Optional, List

from app.schemas.ability import AbilityRead
from app.schemas.race import RaceRead
from app.schemas.profession import ProfessionRead
from app.schemas.level import LevelRead

class CharacterBase(BaseModel):
    name: str = Field(..., description="Имя персонажа")

    # Вместо одного JSON-«attributes» — теперь игрок вводит САМ
    # базовые значения (например, до бонусов): strength_user, dexterity_user, …
    strength_user: int = Field(..., description="«Сырой» показатель Силы, до применения бонусов")
    dexterity_user: int = Field(..., description="«Сырой» показатель Ловкости")
    constitution_user: int = Field(..., description="«Сырой» показатель Телосложения")
    intelligence_user: int = Field(..., description="«Сырой» показатель Интеллекта")
    wisdom_user: int = Field(..., description="«Сырой» показатель Мудрости")
    charisma_user: int = Field(..., description="«Сырой» показатель Харизмы")

    race_id: int = Field(..., description="ID расы (из списка /races)")
    profession_id: int = Field(..., description="ID профессии (класса)")
    level_id: int = Field(..., description="ID уровня (из списка /levels)")

    is_npc: bool = Field(default=False, description="Является ли NPC")
    avatar_url: Optional[str] = Field(None, description="URL аватара персонажа")

class CharacterCreate(CharacterBase):
    ability_ids: Optional[List[int]] = Field(
        default_factory=list,
        description="Список ID способностей для присвоения"
    )
    session_id: Optional[int] = Field(None, description="ID сессии, если персонаж участвует")

class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Новое имя персонажа")
    session_id: Optional[int] = Field(None, description="Обновлённый ID сессии")
    strength_user: Optional[int] = None
    dexterity_user: Optional[int] = None
    constitution_user: Optional[int] = None
    intelligence_user: Optional[int] = None
    wisdom_user: Optional[int] = None
    charisma_user: Optional[int] = None

    race_id: Optional[int] = None
    profession_id: Optional[int] = None
    level_id: Optional[int] = None

    ability_ids: Optional[List[int]] = None
    is_npc: Optional[bool] = None
    avatar_url: Optional[str] = None

class CharacterRead(BaseModel):
    id: int = Field(..., description="ID персонажа")
    name: str
    player_id: int
    session_id: Optional[int]

    # Теперь мы хотим возвращать не «race_id», а уже всю RaceRead
    race: RaceRead
    # и тоже для класса:
    profession: ProfessionRead = Field(..., alias="profession")
    # и информация про уровень:
    level: LevelRead = Field(..., alias="level_ref")

    hp: int
    armor: int
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    is_npc: bool
    avatar_url: Optional[str] = None

    abilities: List[AbilityRead] = Field(default_factory=list)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True  # чтобы alias="class_ref" работал
