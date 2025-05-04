from pydantic import BaseModel, Field

class EventTemplate(BaseModel):
    id: int = Field(..., description="Уникальный ID шаблона события")
    title: str = Field(..., description="Короткое название события")
    description: str = Field(..., description="Подробное описание события")
    severity: str = Field(..., description="Степень важности события (низкая, средняя, высокая)")
