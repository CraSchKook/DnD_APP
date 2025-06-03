from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.schemas.player import Player
from app.models.player import Player as PlayerModel  # реальная модель
from app.core.auth import get_current_user

router = APIRouter(
    prefix="/players",
    tags=["Players"]
)

@router.get("/me")
async def read_myself(current_user: PlayerModel = Depends(get_current_user)):
    """
    Возвращает информацию о текущем (залогиненном через Telegram) игроке.
    get_current_user достанет JWT из заголовка и найдёт нужного PlayerModel.
    """
    return {
        "id": current_user.id,
        "telegram_id": current_user.telegram_id,
        "name": current_user.name,
        "username": current_user.username,
        "role": current_user.role,              #
        "active_as": current_user.active_as     # ← Как Мастер или Игрок в данный момент
    }

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

@router.post("/switch_role")
async def switch_active_role(
    new_role: str,
    current_user: PlayerModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Переключить активную роль: 'player' или 'master'.

    Доступ к 'master' разрешён только если роль = master (есть подписка).
    """
    if new_role not in ("player", "master"):
        raise HTTPException(status_code=400, detail="Invalid role. Use 'player' or 'master'.")

    if new_role == "master" and current_user.role != "master":
        raise HTTPException(status_code=403, detail="You are not allowed to act as a Master.")

    current_user.active_as = new_role
    await db.commit()
    return {"message": f"Now acting as {new_role}"}