from typing import List
from fastapi import HTTPException
from app.schemas.effect import Effect
from app.schemas.event_instance import EventInstance

class FakeEffectDatabase:
    """In-memory хранилище эффектов."""
    def __init__(self):
        self._effects: List[Effect] = []

    def list_effects(self) -> List[Effect]:
        return self._effects

    def get_effect(self, effect_id: int) -> Effect:
        for e in self._effects:
            if e.id == effect_id:
                return e
        raise HTTPException(status_code=404, detail="Effect not found")

    def create_effect(self, effect: Effect) -> Effect:
        if any(e.id == effect.id for e in self._effects):
            raise HTTPException(status_code=400, detail="Effect with this ID already exists")
        self._effects.append(effect)
        return effect

    def update_effect(self, effect_id: int, updated: Effect) -> Effect:
        for idx, e in enumerate(self._effects):
            if e.id == effect_id:
                self._effects[idx] = updated
                return updated
        raise HTTPException(status_code=404, detail="Effect not found")

    def delete_effect(self, effect_id: int) -> None:
        for idx, e in enumerate(self._effects):
            if e.id == effect_id:
                self._effects.pop(idx)
                return
        raise HTTPException(status_code=404, detail="Effect not found")

fake_effect_db = FakeEffectDatabase()

def get_effect_db() -> FakeEffectDatabase:
    """Dependency для работы с эффектами."""
    return fake_effect_db
