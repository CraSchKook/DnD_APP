from typing import List
from fastapi import HTTPException
from app.schemas.event_template import EventTemplate

class FakeEventTemplateDatabase:
    """In-memory хранилище шаблонов событий."""
    def __init__(self):
        self._templates: List[EventTemplate] = []

    def list_templates(self) -> List[EventTemplate]:
        return self._templates

    def get_template(self, template_id: int) -> EventTemplate:
        for t in self._templates:
            if t.id == template_id:
                return t
        raise HTTPException(status_code=404, detail="EventTemplate not found")

    def create_template(self, template: EventTemplate) -> EventTemplate:
        if any(t.id == template.id for t in self._templates):
            raise HTTPException(status_code=400, detail="Template with this ID already exists")
        self._templates.append(template)
        return template

    def update_template(self, template_id: int, updated: EventTemplate) -> EventTemplate:
        for idx, t in enumerate(self._templates):
            if t.id == template_id:
                self._templates[idx] = updated
                return updated
        raise HTTPException(status_code=404, detail="EventTemplate not found")

    def delete_template(self, template_id: int) -> None:
        for idx, t in enumerate(self._templates):
            if t.id == template_id:
                self._templates.pop(idx)
                return
        raise HTTPException(status_code=404, detail="EventTemplate not found")

fake_event_template_db = FakeEventTemplateDatabase()

def get_event_template_db() -> FakeEventTemplateDatabase:
    """Dependency для работы с шаблонами событий."""
    return fake_event_template_db
