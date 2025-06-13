from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union

class AbilityBase(BaseModel):
    name: str = Field(..., description="Название способности")
    description: Optional[str] = Field("", description="Описание")
    cooldown: float = Field(0.0, description="Время перезарядки в секундах")
    
    # Условия активации: объект или список объектов
    activation_condition: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None, 
        description=(
            "Условия вызова абилки, можно передать JSON-объект или массив JSON-объектов, например:"
            "[{ 'requires_shards': {'white':1} }, { 'uses_per_long_rest':1 }]")
    )

    model_config = {"from_attributes": True}

class AbilityCreate(AbilityBase):
    allowed_race_names: Optional[List[str]] = Field(
        default_factory=list,
        description="Названия рас, которым доступна способность"
    )
    allowed_profession_names: Optional[List[str]] = Field(
        default_factory=list,
        description="Названия классов, которым доступна способность"
    )
    character_ids: Optional[List[int]] = Field(
        default_factory=list,
        description="ID персонажей, кому выдать способность"
    )


class AbilityUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Новое название способности")
    description: Optional[str] = Field(None, description="Новое описание")
    cooldown: Optional[float] = Field(None, description="Новое значение перезарядки")
    allowed_race_names: Optional[List[str]] = Field(
        default=None,
        description="Обновлённый список рас по названиям"
    )
    allowed_profession_names: Optional[List[str]] = Field(
        default=None,
        description="Обновлённый список классов по названиям"
    )
    character_ids: Optional[List[int]] = Field(
        default=None,
        description="Список ID персонажей для связи"
    )

    activation_condition: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(None, description="Новые условия вызова абилки")
    model_config = {"from_attributes": True}

class AbilityRead(AbilityBase):
    id: int = Field(..., description="ID способности")
    allowed_races: List[str] = Field(default_factory=list, description="Названия рас, которым доступна способность")
    allowed_professions: List[str] = Field(default_factory=list, description="Названия классов, которым доступна способность")
    character_ids: List[int] = Field(default_factory=list, description="ID персонажей, у которых есть способность")

    activation_condition: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(None, description="Условия вызова абилки")
    model_config = {"from_attributes": True}
