from pydantic import BaseModel, Field
from typing import Optional

# --------------------------------------------
# PlayerCreate/PlayerUpdate/PlayerRead схемы
# --------------------------------------------

class PlayerBase(BaseModel):
    """
    Базовая схема для Player: общие поля.
    """
    telegram_id: int = Field(..., description="Telegram ID игрока")
    name: str = Field(..., description="Имя игрока")
    username: Optional[str] = Field(None, description="Username Telegram (если есть)")
    role: Optional[str] = Field("player", description="Роль аккаунта: 'player' или 'master'")
    active_as: Optional[str] = Field("player", description="Текущий режим: 'player' или 'master'")

    model_config = {
        "from_attributes": True  # чтобы модель могла читать атрибуты из SQLAlchemy-объекта
    }

class PlayerUpdate(BaseModel):
    """
    Схема для обновления Player.
    Можно передавать любую комбинацию полей для изменения.
    """
    telegram_id: Optional[int] = Field(None, description="Telegram ID игрока")
    name: Optional[str] = Field(None, description="Имя игрока")
    username: Optional[str] = Field(None, description="Username Telegram (если есть)")
    role: Optional[str] = Field(None, description="Роль аккаунта: 'player' или 'master'")
    active_as: Optional[str] = Field(None, description="Текущий режим: 'player' или 'master'")

    model_config = {
        "from_attributes": True
    }

class PlayerRead(PlayerBase):
    """
    Схема для чтения Player. Все поля обязательны в ответе, включая id.
    """
    id: int = Field(..., description="ID игрока в базе")

    model_config = {
        "from_attributes": True
    }
