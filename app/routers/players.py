from fastapi import APIRouter, Depends
from app.dependencies.db import FakeDatabase, get_db
from app.schemas.player import Player

router = APIRouter(
    prefix="/players",
    tags=["Players"]
)

@router.get("/", response_model=list[Player])
async def get_players(db: FakeDatabase = Depends(get_db)):
    """Вернуть всех игроков."""
    return db.list_players()

@router.get("/{player_id}", response_model=Player)
async def get_player(player_id: int, db: FakeDatabase = Depends(get_db)):
    """Вернуть одного игрока по ID."""
    return db.get_player(player_id)

@router.post("/", response_model=Player, status_code=201)
async def create_player(player: Player, db: FakeDatabase = Depends(get_db)):
    """Создать нового игрока."""
    return db.create_player(player)

@router.put("/{player_id}", response_model=Player)
async def update_player(
    player_id: int,
    updated: Player,
    db: FakeDatabase = Depends(get_db)
):
    """Обновить данные игрока."""
    return db.update_player(player_id, updated)

@router.delete("/{player_id}", status_code=204)
async def delete_player(player_id: int, db: FakeDatabase = Depends(get_db)):
    """Удалить игрока."""
    db.delete_player(player_id)
    return
