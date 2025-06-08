from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import engine, Base, async_session_maker

# Подключаем все модели, чтобы они попали в metadata
import app.models.player
import app.models.session
import app.models.character
import app.models.item
import app.models.ability
import app.models.map
import app.models.map_object
import app.models.effect
import app.models.event_template
import app.models.inventory
import app.models.theme

# Импорт seed-функций
from app.seed.races import seed_races
from app.seed.professions import seed_professions
from app.seed.levels import seed_levels
from app.seed.abilities import seed_abilities

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    1. Создание всех таблиц (Base.metadata.create_all)
    2. Заполнение стартовыми данными (races, professions, levels), если их нет
    3. Запуск FastAPI
    """
    print("→ Создаю таблицы...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✔ Таблицы созданы.")

    async with async_session_maker() as db:
        await seed_races(db)
        await seed_professions(db)
        await seed_levels(db)
        await seed_abilities(db)
    print("✔ Seed-данные загружены.")
    yield

app = FastAPI(lifespan=lifespan)

# Разрешение адресов для запросов
origins = [
    "http://localhost:5173", # локальный сервер дев
    "http://localhost:4173/", # локальный сервер билда
    "https://mini.shadstar.ru",
    "https://t.me/Shadowstar_master_bot"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # разрешенные адреса
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем каталог 'static' на URL '/static'
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- Подключение всех роутеров ---
from app.routers.auth import router as auth_router
from app.routers.players import router as players_router
from app.routers.sessions import router as sessions_router
from app.routers.races import router as races_router
from app.routers.profession import router as professions_router
from app.routers.levels import router as levels_router
from app.routers.characters import router as characters_router
from app.routers.items import router as items_router
from app.routers.abilities import router as abilities_router
from app.routers.maps import router as maps_router
from app.routers.map_objects import router as map_objects_router
from app.routers.effects import router as effects_router
from app.routers.event_templates import router as event_templates_router
from app.routers.inventory import router as inventory_router
from app.routers.event_instance import router as event_instance_router
from app.routers.theme import router as theme_router

app.include_router(auth_router)
app.include_router(players_router)
app.include_router(sessions_router)
app.include_router(races_router)
app.include_router(professions_router)
app.include_router(levels_router)
app.include_router(characters_router)
app.include_router(items_router)
app.include_router(abilities_router)
app.include_router(maps_router)
app.include_router(map_objects_router)
app.include_router(effects_router)
app.include_router(event_templates_router)
app.include_router(inventory_router)
app.include_router(event_instance_router)
app.include_router(theme_router)


# --- Web-интерфейс (страница с WebSocket) ---
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>D&D App</title></head>
        <body>
            <h1>Привет! Это D&D приложение</h1>
            <button onclick="sendMessage()">Отправить сообщение на сервер</button>
            <div id="messages"></div>
            <script>
                const ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + "/ws");
                ws.onmessage = function(event) {
                    const messages = document.getElementById('messages');
                    const message = document.createElement('div');
                    message.textContent = 'Новое сообщение: ' + event.data;
                    messages.appendChild(message);
                };
                function sendMessage() {
                    ws.send("Привет серверу!");
                }
            </script>
        </body>
    </html>
    """


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Простое WebSocket-соединение, принимает и отправляет текст.
    """
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Сообщение получено: {data}")
