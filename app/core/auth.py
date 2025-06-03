from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.player import Player as PlayerModel
import os
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET = "a1890eb396e2d48d530ef0071345a5f7567819895e7e44871885b2357e56bb6d" #os.getenv("JWT_SECRET") 
JWT_ALGORITHM = "HS256"

oauth2_scheme = HTTPBearer(bearerFormat="JWT")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> PlayerModel:
    """
    1) Забирает токен из заголовка Authorization: Bearer <token>
    2) Расшифровывает (jwt.decode); если не прошёл — кидает HTTPException(403)
    3) Берёт из payload['sub'] = user_id
    4) Вытягивает из БД PlayerModel по этому ID; если нет — 404
    5) Возвращает объект PlayerModel (SQLAlchemy) — «текущий пользователь»
    """
    token = credentials.credentials  # строка токена без "Bearer "
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    result = await db.execute(select(PlayerModel).where(PlayerModel.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
