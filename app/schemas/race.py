from pydantic import BaseModel, Field
from typing import List

class RaceBase(BaseModel):
    name: str = Field(..., description="Название расы")

    strength_bonus: int = Field(0, description="Бонус к Силе")
    dexterity_bonus: int = Field(0, description="Бонус к Ловкости")
    constitution_bonus: int = Field(0, description="Бонус к Телосложению")
    intelligence_bonus: int = Field(0, description="Бонус к Интеллекту")
    wisdom_bonus: int = Field(0, description="Бонус к Мудрости")
    charisma_bonus: int = Field(0, description="Бонус к Харизме")

    # Новые поля:
    extra_hp: int = Field(2, description="Дополнительное HP (на старте и при каждом уровне)")
    movement_speed: int = Field(30, description="Скорость перемещения (в футах)")
    night_vision: bool = Field(False, description="Ночное зрение (True/False)")
    resistances: List[str] = Field(default_factory=list, description="Устойчивости, пример: ['fire']")
    languages: List[str] = Field(default_factory=list, description="Известные языки, пример: ['Common', 'Elvish']")
    traits: List[str] = Field(default_factory=list, description="Уникальные черты (пассивки), пример: ['Lucky', 'Brave']")

class RaceCreate(RaceBase):
    pass

class RaceRead(RaceBase):
    id: int = Field(..., description="ID расы")

    class Config:
        orm_mode = True
