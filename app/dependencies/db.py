from typing import List
from fastapi import HTTPException

from app.schemas.event_instance import EventInstance
from app.models.theme import Theme as ThemeModel

class FakeDatabase:
    """
    Простейшая in-memory «база» для тем и для инстансов событий.
    """

    def __init__(self):
        # Список Pydantic-моделей EventInstance (из app/schemas/event_instance.py)
        self.event_instances: List[EventInstance] = []
        # Список SQLAlchemy-моделей ThemeModel (из app/models/theme.py)
        self.themes: List[ThemeModel] = []

    # ------------- Theme Methods -------------
    def list_themes(self) -> List[ThemeModel]:
        return self.themes

    def create_theme(self, theme: ThemeModel) -> ThemeModel:
        self.themes.append(theme)
        return theme

    # ------------- EventInstance Methods -------------
    def list_event_instances(self) -> List[EventInstance]:
        return self.event_instances

    def create_event_instance(self, event_instance: EventInstance) -> EventInstance:
        self.event_instances.append(event_instance)
        return event_instance

# Единый экземпляр «фейковой» базы
fake_db = FakeDatabase()

# Функция-зависимость для FastAPI (для роутеров event_instance и theme)
def get_db() -> FakeDatabase:
    return fake_db
