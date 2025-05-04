from typing import List
from fastapi import HTTPException
from app.schemas.ability import Ability

class FakeAbilityDatabase:
    """In-memory хранилище способностей."""
    def __init__(self):
        self._abilities: List[Ability] = []

    def list_abilities(self) -> List[Ability]:
        return self._abilities

    def get_ability(self, ability_id: int) -> Ability:
        for a in self._abilities:
            if a.id == ability_id:
                return a
        raise HTTPException(status_code=404, detail="Ability not found")

    def create_ability(self, ability: Ability) -> Ability:
        if any(a.id == ability.id for a in self._abilities):
            raise HTTPException(status_code=400, detail="Ability with this ID already exists")
        self._abilities.append(ability)
        return ability

    def update_ability(self, ability_id: int, updated: Ability) -> Ability:
        for idx, a in enumerate(self._abilities):
            if a.id == ability_id:
                self._abilities[idx] = updated
                return updated
        raise HTTPException(status_code=404, detail="Ability not found")

    def delete_ability(self, ability_id: int) -> None:
        for idx, a in enumerate(self._abilities):
            if a.id == ability_id:
                self._abilities.pop(idx)
                return
        raise HTTPException(status_code=404, detail="Ability not found")

fake_ability_db = FakeAbilityDatabase()

def get_ability_db() -> FakeAbilityDatabase:
    """Dependency для работы со способностями."""
    return fake_ability_db
