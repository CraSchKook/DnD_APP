from typing import List
from fastapi import HTTPException
from app.schemas.npc import NPC

class FakeNPCDatabase:
    """In-memory хранилище NPC."""
    def __init__(self):
        self._npcs: List[NPC] = []

    def list_npcs(self) -> List[NPC]:
        return self._npcs

    def get_npc(self, npc_id: int) -> NPC:
        for npc in self._npcs:
            if npc.id == npc_id:
                return npc
        raise HTTPException(status_code=404, detail="NPC not found")

    def create_npc(self, npc: NPC) -> NPC:
        if any(n.id == npc.id for n in self._npcs):
            raise HTTPException(status_code=400, detail="NPC with this ID already exists")
        self._npcs.append(npc)
        return npc

    def update_npc(self, npc_id: int, updated: NPC) -> NPC:
        for idx, npc in enumerate(self._npcs):
            if npc.id == npc_id:
                self._npcs[idx] = updated
                return updated
        raise HTTPException(status_code=404, detail="NPC not found")

    def delete_npc(self, npc_id: int) -> None:
        for idx, npc in enumerate(self._npcs):
            if npc.id == npc_id:
                self._npcs.pop(idx)
                return
        raise HTTPException(status_code=404, detail="NPC not found")

fake_npc_db = FakeNPCDatabase()

def get_npc_db() -> FakeNPCDatabase:
    """Dependency для работы с NPC."""
    return fake_npc_db
