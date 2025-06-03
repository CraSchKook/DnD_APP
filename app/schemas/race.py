from pydantic import BaseModel, Field

class RaceBase(BaseModel):
    name: str = Field(..., description="Название расы")
    strength_bonus: int = Field(0, description="Бонус к Силе (Strength)")
    dexterity_bonus: int = Field(0, description="Бонус к Ловкости (Dexterity)")
    constitution_bonus: int = Field(0, description="Бонус к Телосложению (Constitution)")
    intelligence_bonus: int = Field(0, description="Бонус к Интеллекту (Intelligence)")
    wisdom_bonus: int = Field(0, description="Бонус к Мудрости (Wisdom)")
    charisma_bonus: int = Field(0, description="Бонус к Харизме (Charisma)")

class RaceCreate(RaceBase):
    pass

class RaceRead(RaceBase):
    id: int = Field(..., description="ID расы")

    class Config:
        orm_mode = True
