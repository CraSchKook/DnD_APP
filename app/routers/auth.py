from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict
import hmac, hashlib
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.player import Player as PlayerModel
from jose import jwt  # pip install python-jose
from datetime import datetime, timedelta
from dotenv import load_dotenv # секреты
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

class TelegramInitData(BaseModel):
    initData: str  # строка вида "id=…&first_name=…&...&hash=…"

# Секреты (можно положить в .env и импортировать через os.getenv)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
JWT_SECRET = "a1890eb396e2d48d530ef0071345a5f7567819895e7e44871885b2357e56bb6d" #os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

def verify_telegram_hash(init_data: str) -> Dict[str, str]:
    """
    Принимаем строку init_data (например, "auth_date=...&id=...&first_name=...&hash=...").
    Проверяем, что hash корректен (HMAC-SHA256 над остальными парами key=value, отсортированными по ключам),
    секретный ключ для HMAC = SHA256(bot_token).
    Если всё ок, возвращаем словарь params без ключа 'hash'.
    Если некорректно — бросаем HTTPException(403).
    """
    # 1) Парсим пары "key=value"
    params = dict(pair.split("=", 1) for pair in init_data.split("&"))
    if "hash" not in params:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No hash in initData")

    received_hash = params.pop("hash")

    # 2) Строим check_string: сортируем ключи, каждый "key=value" в новой строке
    data_check_arr = []
    for key in sorted(params.keys()):
        data_check_arr.append(f"{key}={params[key]}")
    check_string = "\n".join(data_check_arr).encode("utf-8")

    # 3) Считаем секретный ключ: SHA256(bot_token)
    secret_key = hashlib.sha256(BOT_TOKEN.encode("utf-8")).digest()

    # 4) Вычисляем HMAC-SHA256 от check_string
    hmac_obj = hmac.new(secret_key, check_string, hashlib.sha256)
    calculated_hash = hmac_obj.hexdigest()

    # 5) Сравниваем безопасно
    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid auth data")

    return params  # словарь без 'hash': {'id': '123456789', 'first_name': 'Ivan', 'username': 'ivan123', ...}

@router.post("/telegram", response_model=Dict[str, str])
async def telegram_auth(
    data: TelegramInitData,
    db: AsyncSession = Depends(get_db)
):
    # 1) Проверяем подпись
    params = verify_telegram_hash(data.initData)

    # 2) Извлекаем из params
    telegram_id = int(params["id"])
    first_name = params.get("first_name", "")
    username = params.get("username")

    # 3) Ищем в БД
    result = await db.execute(select(PlayerModel).where(PlayerModel.telegram_id == telegram_id))
    player = result.scalar_one_or_none()

    if player is None:
        # 4) Если нет — создаём
        new_player = PlayerModel(
            telegram_id=telegram_id,
            name=first_name,
            username=username,
            role="player"  # ← или "master" при необходимости
        )
        db.add(new_player)
        await db.commit()
        await db.refresh(new_player)
        user_id = new_player.id
    else:
        # 5) Если есть — обновим, на всякий случай, имя/username
        user_id = player.id
        if player.name != first_name or player.username != username:
            player.name = first_name
            player.username = username
            await db.commit()

    # 6) Генерируем JWT (срок жизни, например, 7 дней)
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}