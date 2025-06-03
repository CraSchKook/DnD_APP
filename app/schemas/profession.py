from pydantic import BaseModel, Field

class ProfessionBase(BaseModel):
    name: str = Field(..., description="Название класса (Fighter, Rogue, и т. д.)")
    hit_die: int = Field(8, description="lый куб здоровья, который даёт класс (например, 10 для Fighter)")
    strength_bonus: int = Field(0, description="Бонус к Силе")
    dexterity_bonus: int = Field(0, description="Бонус к Ловкости")
    constitution_bonus: int = Field(0, description="Бонус к Телосложению")
    intelligence_bonus: int = Field(0, description="Бонус к Интеллекту")
    wisdom_bonus: int = Field(0, description="Бонус к Мудрости")
    charisma_bonus: int = Field(0, description="Бонус к Харизме")

class ProfessionCreate(ProfessionBase):
    pass

class ProfessionRead(ProfessionBase):
    id: int = Field(..., description="ID класса")

    class Config:
        orm_mode = True
