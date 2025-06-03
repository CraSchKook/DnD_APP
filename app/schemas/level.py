from pydantic import BaseModel, Field

class LevelBase(BaseModel):
    hp_increase: int = Field(..., description="Сколько HP добавляется при достижении этого уровня")
    bonus_attribute: str = Field(None, description="Какой атрибут можно улучшить (+1)")
    description: str = Field("", description="Текстовое описание бонусов уровня")

class LevelCreate(LevelBase):
    id: int = Field(..., description="Номер уровня")  # Например, 1, 2, 3

class LevelRead(LevelBase):
    id: int = Field(..., description="Уникальный идентификатор уровня (сам номер уровня)")

    class Config:
        orm_mode = True
