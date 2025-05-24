from pydantic import BaseModel, Field
from typing import Literal, Optional

class EffectBase(BaseModel):
    target_type: Literal["character", "session"] = Field(..., description="Тип цели эффекта")
    target_id:   int                             = Field(..., description="ID цели эффекта")
    name:        str                             = Field(..., description="Название эффекта")
    duration:    float                           = Field(0.0, description="Длительность эффекта в секундах")

class EffectUpdate(BaseModel):
    name:        Optional[str]     = Field(None, description="Новое имя эффекта")
    duration:    Optional[float]   = Field(None, description="Новая длительность в секундах")
    # Можно также позволить менять target_type/target_id, если нужно:
    target_type: Optional[Literal["character","session"]] = None
    target_id:   Optional[int]     = None

class EffectCreate(EffectBase):
    """Используется при POST /effects/"""
    pass

class EffectRead(EffectBase):
    id: int = Field(..., description="Уникальный ID эффекта")

    class Config:
        from_attributes = True
