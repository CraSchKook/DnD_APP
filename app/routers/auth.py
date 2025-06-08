from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import hmac
import hashlib
import json
import urllib.parse
from jose import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

from app.database import get_db
from app.models.player import Player as PlayerModel

# Загружаем переменные окружения из .env
load_dotenv()
# Токен бота Telegram для проверки подписи
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
print (BOT_TOKEN)
# Секрет для JWT и алгоритм
JWT_SECRET = os.getenv("JWT_SECRET", "a1890eb396e2d48d530ef0071345a5f7567819895e7e44871885b2357e56bb6d")
JWT_ALGORITHM = "HS256"

# Инициализация маршрутизатора FastAPI
router = APIRouter(prefix="/auth", tags=["Auth"])

# Pydantic-модель для тела запроса
class TelegramInitData(BaseModel):
    initData: str  # Строка формата query_id=...&user=...&auth_date=...&hash=...


def verify_telegram_hash(init_data: str) -> dict[str, str]:
    """
    Проверяет подпись Telegram WebApp initData и возвращает словарь параметров.
    При неверной подписи или просроченных данных выбрасывает HTTPException.
    """
    # Парсим строку query string в список пар (ключ, значение)
    try:
        pairs = urllib.parse.parse_qsl(init_data, keep_blank_values=True, strict_parsing=True)
        params: dict[str, str] = dict(pairs)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный формат initData")

    # Извлекаем и удаляем hash из параметров
    received_hash = params.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Отсутствует параметр hash")

    # Проверяем дату auth_date (максимум 24 часа, чтобы предотвратить повторные атаки)
    auth_ts = params.get("auth_date")
    if auth_ts:
        try:
            # Переводим timestamp в datetime UTC
            auth_date = datetime.fromtimestamp(int(auth_ts), tz=timezone.utc)
            now = datetime.now(tz=timezone.utc)
            if (now - auth_date).total_seconds() > 86400:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Данные аутентификации устарели")
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный формат auth_date")

    # Строим строку для проверки: ключ=значение, отсортированные по ключу, каждая пара в новой строке
    data_check_arr = [f"{k}={params[k]}" for k in sorted(params.keys())]
    data_check_string = "\n".join(data_check_arr).encode('utf-8')

    # Убеждаемся, что BOT_TOKEN задан
    if not BOT_TOKEN:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка конфигурации сервера: нет BOT_TOKEN")
    # Генерируем секретный ключ: SHA256 от BOT_TOKEN
    secret_key = hashlib.sha256(BOT_TOKEN.encode('utf-8')).digest()
    # Вычисляем HMAC-SHA256
    calc_hash = hmac.new(secret_key, data_check_string, hashlib.sha256).hexdigest()

    # Сравниваем вычисленный и полученный хэши в безопасном режиме
    if not hmac.compare_digest(calc_hash, received_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Неверные данные аутентификации Telegram")

    return params


@router.post("/telegram", response_model=dict)
async def telegram_auth(
    data: TelegramInitData = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Маршрут для аутентификации через Telegram WebApp.
    Создает или обновляет пользователя в БД и возвращает JWT.
    """
    # Проверяем initData и получаем параметры
    params = verify_telegram_hash(data.initData)

    # Извлекаем информацию о пользователе:
    # если есть поле 'user', то оно содержит JSON, иначе данные идут в прямых полях
    if "user" in params:
        try:
            user_info = json.loads(urllib.parse.unquote_plus(params['user']))
        except json.JSONDecodeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный JSON в поле user")
    else:
        user_info = params

    # Получаем необходимые поля пользователя
    try:
        telegram_id = int(user_info.get('id', params.get('id')))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный Telegram ID пользователя")
    first_name = user_info.get('first_name') or params.get('first_name', '')
    username = user_info.get('username') or params.get('username')

    # Ищем существующего игрока в БД по telegram_id
    try:
        result = await db.execute(select(PlayerModel).where(PlayerModel.telegram_id == telegram_id))
        player = result.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка БД: {e}")

    if not player:
        # Если игрока нет, создаем нового
        player = PlayerModel(
            telegram_id=telegram_id,
            name=first_name,
            username=username,
            role="player"
        )
        db.add(player)
    else:
        # Если игрок есть, обновляем имя/username при изменениях
        updated = False
        if player.name != first_name:
            player.name = first_name
            updated = True
        if player.username != username:
            player.username = username
            updated = True
        if updated:
            db.add(player)

    # Сохраняем изменения в БД
    try:
        await db.commit()
        await db.refresh(player)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при сохранении в БД: {e}")

    # Генерируем JWT токен на 7 дней
    expire = datetime.now(tz=timezone.utc) + timedelta(days=7)
    token = jwt.encode({"sub": str(player.id), "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # Возвращаем токен
    return {"access_token": token, "token_type": "bearer"}