from typing import List
from fastapi import HTTPException
from app.schemas.map_object import MapObject

class FakeMapObjectDatabase:
    """In-memory хранилище объектов карты."""
    def __init__(self):
        self._objects: List[MapObject] = []

    def list_objects(self) -> List[MapObject]:
        return self._objects

    def get_object(self, object_id: int) -> MapObject:
        for obj in self._objects:
            if obj.id == object_id:
                return obj
        raise HTTPException(status_code=404, detail="MapObject not found")

    def create_object(self, obj: MapObject) -> MapObject:
        if any(o.id == obj.id for o in self._objects):
            raise HTTPException(status_code=400, detail="Object with this ID already exists")
        self._objects.append(obj)
        return obj

    def update_object(self, object_id: int, updated: MapObject) -> MapObject:
        for idx, o in enumerate(self._objects):
            if o.id == object_id:
                self._objects[idx] = updated
                return updated
        raise HTTPException(status_code=404, detail="MapObject not found")

    def delete_object(self, object_id: int) -> None:
        for idx, o in enumerate(self._objects):
            if o.id == object_id:
                self._objects.pop(idx)
                return
        raise HTTPException(status_code=404, detail="MapObject not found")

fake_map_object_db = FakeMapObjectDatabase()

def get_map_object_db() -> FakeMapObjectDatabase:
    """Dependency для работы с объектами карты."""
    return fake_map_object_db
