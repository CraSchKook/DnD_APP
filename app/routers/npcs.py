from fastapi import APIRouter, Depends
from app.schemas.npc import NPC
from app.dependencies.npc_db import FakeNPCDatabase, get_npc_db

router = APIRouter(
    prefix="/npcs",
    tags=["NPCs"]
)

@router.get("/", response_model=list[NPC])
async def get_npcs(db: FakeNPCDatabase = Depends(get_npc_db)):
    return db.list_npcs()

@router.get("/{npc_id}", response_model=NPC)
async def get_npc(npc_id: int, db: FakeNPCDatabase = Depends(get_npc_db)):
    return db.get_npc(npc_id)

@router.post("/", response_model=NPC, status_code=201)
async def create_npc(npc: NPC, db: FakeNPCDatabase = Depends(get_npc_db)):
    return db.create_npc(npc)

@router.put("/{npc_id}", response_model=NPC)
async def update_npc(npc_id: int, updated: NPC, db: FakeNPCDatabase = Depends(get_npc_db)):
    return db.update_npc(npc_id, updated)

@router.delete("/{npc_id}", status_code=204)
async def delete_npc(npc_id: int, db: FakeNPCDatabase = Depends(get_npc_db)):
    db.delete_npc(npc_id)
    return
