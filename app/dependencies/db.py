#удалить когда придет время

from typing import List
from fastapi import HTTPException
from app.schemas.player import Player
from app.models.inventory import Inventory as InventoryModel
from app.schemas.event_instance import EventInstance
from app.models.theme import Theme as ThemeModel

class FakeDatabase:
    """Простая in-memory база для проекта."""

    def __init__(self):
        self._players: List[Player] = []
        self.inventories: List[InventoryModel] = []  # Инвентари
        self.event_instances: List[EventInstance] = []  # События
        self.themes: List[ThemeModel] = []  # ← Темы

    # ----------------- Player Methods -----------------

    def list_players(self) -> List[Player]:
        return self._players

    def get_player(self, player_id: int) -> Player:
        for p in self._players:
            if p.id == player_id:
                return p
        raise HTTPException(status_code=404, detail="Player not found")

    def create_player(self, player: Player) -> Player:
        if any(p.id == player.id for p in self._players):
            raise HTTPException(status_code=400, detail="Player with this ID already exists")
        self._players.append(player)
        return player

    def update_player(self, player_id: int, updated: Player) -> Player:
        for idx, p in enumerate(self._players):
            if p.id == player_id:
                self._players[idx] = updated
                return updated
        raise HTTPException(status_code=404, detail="Player not found")

    def delete_player(self, player_id: int) -> None:
        for idx, p in enumerate(self._players):
            if p.id == player_id:
                self._players.pop(idx)
                return
        raise HTTPException(status_code=404, detail="Player not found")

    # ----------------- Inventory Methods -----------------
    # (сюда позже добавим методы для работы с InventoryModel)

    # ----------------- Theme Methods -----------------

    def list_themes(self) -> List[ThemeModel]:
        return self.themes

    def create_theme(self, theme: ThemeModel) -> ThemeModel:
        self.themes.append(theme)
        return theme

    # ----------------- EventInstance Methods -----------------

    def list_event_instances(self) -> List[EventInstance]:
        return self.event_instances

    def create_event_instance(self, event_instance: EventInstance) -> EventInstance:
        self.event_instances.append(event_instance)
        return event_instance

# ----------------- Dependency -----------------

# Единый экземпляр базы
fake_db = FakeDatabase()

# Dependency для FastAPI
def get_db() -> FakeDatabase:
    return fake_db
