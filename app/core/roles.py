from fastapi import Depends, HTTPException, status
from app.core.auth import get_current_user
from app.models.player import Player

def require_active_as(expected: str):
    """
    Проверка: пользователь действует в нужной роли (player/master).
    Например: active_as == 'master'
    """
    async def checker(current_user: Player = Depends(get_current_user)):
        if current_user.active_as != expected:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are acting as '{current_user.active_as}', but '{expected}' is required"
            )
        return current_user
    return checker
