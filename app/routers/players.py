from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.schemas.player import Player
from app.models.player import Player as PlayerModel  # реальная модель

router = APIRouter(
    prefix="/players",
    tags=["Players"]
)

@router.get("/", response_model=list[Player])
async def get_players(db: AsyncSession = Depends(get_db)):
    """Вернуть всех игроков."""
    result = await db.execute(select(PlayerModel))
    players = result.scalars().all()
    return players

@router.get("/{player_id}", response_model=Player)
async def get_player(player_id: int, db: AsyncSession = Depends(get_db)):
    """Вернуть одного игрока по ID."""
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.post("/", response_model=Player, status_code=201)
async def create_player(player: Player, db: AsyncSession = Depends(get_db)):
    """Создать нового игрока."""
    new_player = PlayerModel(name=player.name)
    db.add(new_player)
    await db.commit()
    await db.refresh(new_player)
    return new_player

@router.put("/{player_id}", response_model=Player)
async def update_player(player_id: int, updated: Player, db: AsyncSession = Depends(get_db)):
    """Обновить данные игрока."""
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    player.name = updated.name
    await db.commit()
    await db.refresh(player)
    return player

@router.delete("/{player_id}", status_code=204)
async def delete_player(player_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить игрока."""
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    await db.delete(player)
    await db.commit()
