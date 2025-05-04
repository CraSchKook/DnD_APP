from typing import List
from fastapi import HTTPException
from app.schemas.map import Map

class FakeMapDatabase:
    """In-memory хранилище карт."""
    def __init__(self):
        self._maps: List[Map] = []

    def list_maps(self) -> List[Map]:
        return self._maps

    def get_map(self, map_id: int) -> Map:
        for m in self._maps:
            if m.id == map_id:
                return m
        raise HTTPException(status_code=404, detail="Map not found")

    def create_map(self, map_obj: Map) -> Map:
        if any(m.id == map_obj.id for m in self._maps):
            raise HTTPException(status_code=400, detail="Map with this ID already exists")
        self._maps.append(map_obj)
        return map_obj

    def update_map(self, map_id: int, updated: Map) -> Map:
        for idx, m in enumerate(self._maps):
            if m.id == map_id:
                self._maps[idx] = updated
                return updated
        raise HTTPException(status_code=404, detail="Map not found")

    def delete_map(self, map_id: int) -> None:
        for idx, m in enumerate(self._maps):
            if m.id == map_id:
                self._maps.pop(idx)
                return
        raise HTTPException(status_code=404, detail="Map not found")

fake_map_db = FakeMapDatabase()

def get_map_db() -> FakeMapDatabase:
    """Dependency для работы с картами."""
    return fake_map_db
