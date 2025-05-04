from typing import List
from fastapi import HTTPException
from app.schemas.character import Character

class FakeCharacterDatabase:
    """In-memory хранилище персонажей."""
    def __init__(self):
        self._characters: List[Character] = []

    def list_characters(self) -> List[Character]:
        return self._characters

    def get_character(self, character_id: int) -> Character:
        for c in self._characters:
            if c.id == character_id:
                return c
        raise HTTPException(status_code=404, detail="Character not found")

    def create_character(self, character: Character) -> Character:
        if any(c.id == character.id for c in self._characters):
            raise HTTPException(status_code=400, detail="ID already exists")
        self._characters.append(character)
        return character

    def update_character(self, character_id: int, updated: Character) -> Character:
        for idx, c in enumerate(self._characters):
            if c.id == character_id:
                self._characters[idx] = updated
                return updated
        raise HTTPException(status_code=404, detail="Character not found")

    def delete_character(self, character_id: int) -> None:
        for idx, c in enumerate(self._characters):
            if c.id == character_id:
                self._characters.pop(idx)
                return
        raise HTTPException(status_code=404, detail="Character not found")

fake_character_db = FakeCharacterDatabase()

def get_character_db() -> FakeCharacterDatabase:
    """Dependency для работы с персонажами."""
    return fake_character_db
