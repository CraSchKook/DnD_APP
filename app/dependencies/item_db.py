from typing import List
from fastapi import HTTPException
from app.schemas.item import Item

class FakeItemDatabase:
    """In-memory хранилище предметов."""
    def __init__(self):
        self._items: List[Item] = []

    def list_items(self) -> List[Item]:
        return self._items

    def get_item(self, item_id: int) -> Item:
        for i in self._items:
            if i.id == item_id:
                return i
        raise HTTPException(status_code=404, detail="Item not found")

    def create_item(self, item: Item) -> Item:
        if any(i.id == item.id for i in self._items):
            raise HTTPException(status_code=400, detail="Item with this ID already exists")
        self._items.append(item)
        return item

    def update_item(self, item_id: int, updated: Item) -> Item:
        for idx, i in enumerate(self._items):
            if i.id == item_id:
                self._items[idx] = updated
                return updated
        raise HTTPException(status_code=404, detail="Item not found")

    def delete_item(self, item_id: int) -> None:
        for idx, i in enumerate(self._items):
            if i.id == item_id:
                self._items.pop(idx)
                return
        raise HTTPException(status_code=404, detail="Item not found")

fake_item_db = FakeItemDatabase()

def get_item_db() -> FakeItemDatabase:
    """Dependency для работы с предметами."""
    return fake_item_db
