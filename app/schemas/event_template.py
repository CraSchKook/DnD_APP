from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class EventTemplateBase(BaseModel):
    name: str = Field(..., description="Короткое название события")
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None  # можно передавать любые данные

class EventTemplateCreate(EventTemplateBase):
    pass

class EventTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Короткое название события")
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class EventTemplateRead(EventTemplateBase):
    id: int = Field(..., description="Уникальный ID шаблона события")

    class Config:
        from_attributes = True
