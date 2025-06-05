from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.schemas.player import PlayerRead, PlayerUpdate
from app.models.player import Player as PlayerModel
from app.core.auth import get_current_user

router = APIRouter(
    prefix="/players",
    tags=["Players"]
)

@router.get("/me", response_model=PlayerRead)
async def read_myself(
    current_user: PlayerModel = Depends(get_current_user)
):
    """
    Возвращает информацию о текущем (залогиненном через Telegram) игроке.
    get_current_user достанет JWT из заголовка и найдёт нужного PlayerModel.
    """
    return PlayerRead.model_validate(current_user)

@router.get("/", response_model=list[PlayerRead])
async def get_players(db: AsyncSession = Depends(get_db)):
    """
    Вернуть всех игроков.
    """
    result = await db.execute(select(PlayerModel))
    players = result.scalars().all()
    return [PlayerRead.model_validate(p) for p in players]

@router.get("/{player_id}", response_model=PlayerRead)
async def get_player(player_id: int, db: AsyncSession = Depends(get_db)):
    """
    Вернуть одного игрока по ID.
    """
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return PlayerRead.model_validate(player)

@router.put("/{player_id}", response_model=PlayerRead)
async def update_player(
    player_id: int,
    data: PlayerUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить данные игрока:
      - telegram_id,
      - name,
      - username,
      - role (player/master),
      - active_as (player/master).
    """
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    
     # Обновляем каждое поле, если оно было передано
    if data.telegram_id is not None:
        player.telegram_id = data.telegram_id
    if data.name is not None:
        player.name = data.name
    if data.username is not None:
        player.username = data.username
    if data.role is not None:
        # допускаем только 'player' или 'master'
        if data.role not in ("player", "master"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be 'player' or 'master'")
        player.role = data.role
    if data.active_as is not None:
        # допускаем только 'player' или 'master'
        if data.active_as not in ("player", "master"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="active_as must be 'player' or 'master'")
        # если пытаемся switch_active_as в 'master', но у игрока роли нет — ошибка
        if data.active_as == "master" and player.role != "master":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot set active_as='master' if role!='master'")
        player.active_as = data.active_as

    await db.commit()
    await db.refresh(player)
    return PlayerRead.model_validate(player)

@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(player_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удалить игрока.
    """
    result = await db.execute(select(PlayerModel).where(PlayerModel.id == player_id))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
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

    Доступ к 'master' разрешён только если роль = master.
    """
    if new_role not in ("player", "master"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role. Use 'player' or 'master'.")

    if new_role == "master" and current_user.role != "master":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to act as a Master.")

    current_user.active_as = new_role
    await db.commit()
    return {"message": f"Now acting as {new_role}"}