from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import urllib.parse
import hmac
import hashlib
import json
import os
import logging

from app.database import get_db
from app.models.player import Player as PlayerModel

# ---------------- ЛОГГЕР ----------------
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)

# ------------- ЗАГРУЗКА КОНФИГА -------------
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
JWT_SECRET = os.getenv("JWT_SECRET", "").strip()
JWT_ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["Auth"])


class TelegramInitData(BaseModel):
    initData: str  # query_id=...&user=...&auth_date=...&hash=...


def verify_telegram_hash(init_data: str) -> dict[str, str]:
    """
    Проверка подписи Telegram WebApp initData по официальному алгоритму:
    1) parse_qsl (URL-decode всех значений)
    2) Исключаем hash
    3) Формируем data_check_string из всех остальных пар (key=value), сортируем
    4) secret_key = HMAC_SHA256(key="WebAppData", msg=BOT_TOKEN)
    5) calculated_hash = HMAC_SHA256(key=secret_key, msg=data_check_string)
    6) Сравниваем calculated_hash и полученный hash
    """
    logger.info("▶️ initData: %s", init_data)

    if not BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN не задан в окружении")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Server misconfigured")

    # 1) URL-декодируем в словарь
    try:
        params = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
        logger.info("   — Пары после parse_qsl: %s", params)
    except ValueError as e:
        logger.error("❌ Ошибка парсинга initData: %s", e)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid initData format")

    # 2) Извлекаем и удаляем hash
    received_hash = params.pop("hash", None)
    logger.info("   — received_hash: %s", received_hash)
    if not received_hash:
        logger.error("❌ Параметр hash отсутствует")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Missing hash")

    # 3) Собираем массив пар key=value (остальные параметры)
    kv_list = [f"{k}={params[k]}" for k in params.keys()]
    # Если есть signature, оно уже в params и войдёт в массив — это нормально.
    # Логи показывают полный список:
    logger.info("   — Пары для data_check_string (до сортировки): %s", kv_list)

    # 4) Сортируем лексикографически по ключу
    kv_list.sort(key=lambda s: s.split("=", 1)[0])
    logger.info("   — Пары для data_check_string (после сортировки): %s", kv_list)

    # 5) Form data_check_string
    data_check_string = "\n".join(kv_list).encode("utf-8")
    logger.info("   — data_check_string:\n%s", data_check_string.decode("utf-8"))

    # 6) Вычисляем секретный ключ: HMAC_SHA256(key="WebAppData", msg=BOT_TOKEN)
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode("utf-8"), hashlib.sha256).digest()
    logger.info("   — secret_key = HMAC_SHA256('WebAppData', BOT_TOKEN) hex: %s", secret_key.hex())

    # 7) Вычисляем окончательный хеш
    calculated_hash = hmac.new(secret_key, data_check_string, hashlib.sha256).hexdigest()
    logger.info("   — calculated_hash: %s", calculated_hash)

    # 8) Сравниваем
    if not hmac.compare_digest(calculated_hash, received_hash):
        logger.error("❌ Хеши не совпали (calculated != received)")
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid authentication data")

    logger.info("✅ Проверка подписи initData пройдена успешно")
    return params  # возвращаем декодированные params для дальнейшей работы


@router.post("/telegram", response_model=dict)
async def telegram_auth(
    body: TelegramInitData = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Эндпоинт /auth/telegram:
    1. Проверка подписи initData
    2. Извлечение данных user
    3. Создание или обновление записи Player
    4. Генерация и возврат JWT
    """
    logger.info("▶️ Запрос POST /auth/telegram")

    # 1) Валидация initData
    params = verify_telegram_hash(body.initData)

    # 2) Извлечение инфо о пользователе
    raw_user = params.get("user")
    if raw_user:
        try:
            user_info = json.loads(raw_user)
            logger.info("   — Распарсенный user: %s", user_info)
        except Exception as e:
            logger.error("❌ Ошибка JSON.loads(user): %s", e)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid user JSON")
    else:
        user_info = params
        logger.info("   — Используем params как user_info: %s", user_info)

    # 3) Достаём обязательные поля
    try:
        telegram_id = int(user_info.get("id"))
        logger.info("   — telegram_id: %s", telegram_id)
    except Exception as e:
        logger.error("❌ Неверный telegram_id: %s", e)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid Telegram ID")

    first_name = user_info.get("first_name", "")
    username = user_info.get("username")
    logger.info("   — first_name=%s, username=%s", first_name, username)

    # 4) Работа с базой
    try:
        result = await db.execute(select(PlayerModel).where(PlayerModel.telegram_id == telegram_id))
        player = result.scalar_one_or_none()
    except Exception as e:
        logger.error("❌ Ошибка запроса к БД: %s", e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database error")

    if not player:
        logger.info("   — Игрок не найден, создаём запись")
        player = PlayerModel(telegram_id=telegram_id, name=first_name, username=username, role="player")
        db.add(player)
    else:
        logger.info("   — Игрок найден (ID=%s), обновляем если нужно", player.id)
        updated = False
        if player.name != first_name:
            player.name = first_name; updated = True
            logger.info("      • Обновили name")
        if player.username != username:
            player.username = username; updated = True
            logger.info("      • Обновили username")
        if updated:
            db.add(player)

    # 5) Сохраняем
    try:
        logger.info("   — Коммитим изменения")
        await db.commit()
        await db.refresh(player)
        logger.info("   — Коммит успешен")
    except Exception as e:
        logger.error("❌ Ошибка при сохранении: %s", e)
        await db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Database commit error")

    # 6) Генерация JWT
    expire = datetime.now(tz=timezone.utc) + timedelta(days=7)
    token = jwt.encode({"sub": str(player.id), "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    logger.info("   — JWT сгенерирован")

    # 7) Отдаём токен
    logger.info("✅ /auth/telegram успешно завершён")
    return {"access_token": token, "token_type": "bearer"}

##############################################################################################
###                              роутер для веб версии                                     ###
##############################################################################################

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

def verify_telegram_widget_data(params: dict) -> dict:
    """
    Проверяет подпись данных от Telegram Login Widget.
    params: словарь с полями id, first_name, username, auth_date, hash и др.
    """
    if not BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN не задан")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Server misconfigured")

    # Извлекаем hash
    received_hash = params.get("hash")
    if not received_hash:
        logger.error("❌ Параметр hash отсутствует")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Missing hash")

    # Формируем data_check_string: сортируем ключи, исключая hash
    data_check_items = [(k, v) for k, v in params.items() if k != "hash"]
    data_check_items.sort(key=lambda x: x[0])
    data_check_string = "\n".join(f"{k}={v}" for k, v in data_check_items)
    logger.info("data_check_string:\n%s", data_check_string)

    # Вычисляем секретный ключ: SHA256(BOT_TOKEN)
    secret_key = hashlib.sha256(BOT_TOKEN.encode("utf-8")).digest()
    # Вычисляем HMAC-SHA-256
    calculated_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    logger.info("calculated_hash: %s, received_hash: %s", calculated_hash, received_hash)

    if not hmac.compare_digest(calculated_hash, received_hash):
        logger.error("❌ Хеши не совпали")
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid authentication data")

    # Проверяем свежесть данных (например, не старше 24 часов)
    auth_date = int(params.get("auth_date", 0))
    current_time = int(datetime.utcnow().timestamp())
    if current_time - auth_date > 86400:
        logger.error("❌ Данные устарели (auth_date слишком старый)")
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Authentication data is outdated")

    logger.info("✅ Проверка подписи виджета пройдена")
    return params

@router.get("/telegram-widget", response_model=dict)
async def telegram_widget_auth(
    id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    username: str | None = None,
    photo_url: str | None = None,
    auth_date: int = 0,
    hash: str = "",
    db: AsyncSession = Depends(get_db)
):
    """
    Обрабатывает данные от Telegram Login Widget, возвращает JWT-токен.
    Параметры приходят как GET-параметры от редиректа.
    """
    # Формируем словарь параметров
    params = {
        "id": str(id),
        "auth_date": str(auth_date),
        "hash": hash
    }
    if first_name:
        params["first_name"] = first_name
    if last_name:
        params["last_name"] = last_name
    if username:
        params["username"] = username
    if photo_url:
        params["photo_url"] = photo_url

    # Проверяем подпись
    try:
        verified_params = verify_telegram_widget_data(params)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("❌ Неожиданная ошибка: %s", str(e))
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid data")

    # Извлекаем telegram_id
    telegram_id = int(verified_params["id"])

    # Ищем или создаем игрока
    result = await db.execute(
        select(PlayerModel).where(PlayerModel.telegram_id == telegram_id)
    )
    player = result.scalar_one_or_none()

    if not player:
        player = PlayerModel(
            telegram_id=telegram_id,
            name=verified_params.get("first_name", "Unknown"),
            username=verified_params.get("username", None),
            role="player",
            active_as="player"
        )
        db.add(player)
        await db.commit()
        await db.refresh(player)

    # Создаем JWT-токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"sub": str(player.id), "exp": datetime.utcnow() + access_token_expires},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    return {"access_token": access_token, "token_type": "bearer"}