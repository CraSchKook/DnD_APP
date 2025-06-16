from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
import aiofiles
import uuid
from pathlib import Path

from app.core.auth import get_current_user
from app.models.player import Player as PlayerModel

# ------------------------------------------
# Router: /upload
# ------------------------------------------
# Этот файл реализует универсальный роут для загрузки изображений.
# Поддерживаются форматы: JPEG, PNG, GIF.
# Логика:
# 1. Проверяем формат файла.
# 2. Определяем папку для загрузки на основе категории и прав пользователя.
# 3. Асинхронно сохраняем файл на диск (в фоне) для минимальной задержки.
# 4. Возвращаем клиенту URL, по которому можно будет получить изображение.
#
# Пример использования в Postman:
# --------------------------------
# POST http://<HOST>/upload/image/
# Authorization: Bearer <JWT_TOKEN>
# Content-Type: multipart/form-data
#
# Body (form-data):
# - file: [файл изображения]
# - category: abilities | items | effects | maps | themes | characters
# - target_player_id: <telegram_id> (только при category=characters, иначе не передавать)
#
# Ответ:
# {
#   "url": "/static/<путь>/<имя_файла>"
# }
# ------------------------------------------

router = APIRouter(prefix="/upload", tags=["Upload"])

# Корневая папка хранения статики
BASE_STATIC = Path("app/static")
# Категории, доступные только мастеру
MASTER_ONLY = {"abilities", "items", "effects", "maps", "themes"}

async def save_file(path: Path, file: UploadFile):
    """
    Асинхронная функция для записи потока данных UploadFile на диск.
    Запускается в BackgroundTasks, чтобы не блокировать основной event loop.
    """
    async with aiofiles.open(path, "wb") as out_file:
        # Читаем кусками по 64KB
        while chunk := await file.read(1024 * 64):
            await out_file.write(chunk)

@router.post("/image/")
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    category: str = Form(...),
    target_player_id: int | None = Form(None),
    current_user: PlayerModel = Depends(get_current_user)
):
    """
    Универсальный эндпоинт для загрузки изображений.

    Параметры:
    - file: файл изображения (JPEG, PNG, GIF).
    - category: категория загрузки:
        * abilities, items, effects, maps, themes - доступны только мастеру;
        * characters - загрузка аватаров персонажей;
    - target_player_id: telegram_id игрока для category=characters (если не передан, берётся текущий).

    Возвращает JSON с ключом "url" для доступа к сохранённому файлу.
    """
    # 1. Проверка расширения и MIME-типа
    ext = file.filename.rsplit('.', 1)[-1].lower()
    allowed_ext = {"jpg", "jpeg", "png", "gif"}
    if ext not in allowed_ext or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Допустимы только JPEG, PNG или GIF")

    # 2. Определяем директорию загрузки
    if category in MASTER_ONLY:
        # Только мастер может загружать в общие каталоги
        if current_user.active_as != "master":
            raise HTTPException(403, "Только мастер может загружать в эту категорию")
        upload_dir = BASE_STATIC / category

    elif category == "characters":
        # Загрузка аватаров персонажей (как игроков, так и NPC)
        # - Игрок загружает только в свою папку
        # - Мастер может загружать для любых персонажей и NPC; по умолчанию файлы попадут в его личную папку
        pid = target_player_id or current_user.telegram_id
        if current_user.telegram_id != pid and current_user.active_as != "master":
            raise HTTPException(403, "Нельзя загружать для другого игрока или NPC")
        upload_dir = BASE_STATIC / "player_uploads" / str(pid) / "characters"
        # Игрок может загружать только в свою папку, мастер в любую
        pid = target_player_id or current_user.telegram_id
        if current_user.telegram_id != pid and current_user.active_as != "master":
            raise HTTPException(403, "Нельзя загружать для другого игрока")
        upload_dir = BASE_STATIC / "player_uploads" / str(pid) / "characters"

    else:
        raise HTTPException(400, f"Неизвестная категория: {category}")

    # Создаём директорию, если её нет
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 3. Формируем уникальное имя файла
    unique_name = f"{uuid.uuid4()}.{ext}"
    destination = upload_dir / unique_name

    # 4. Сохраняем файл в фоне, чтобы ускорить ответ
    background_tasks.add_task(save_file, destination, file)

    # 5. Формируем публичный URL и возвращаем клиенту
    url = str(destination).replace(str(BASE_STATIC), "/static").replace("\\", "/")
    return {"url": url}
