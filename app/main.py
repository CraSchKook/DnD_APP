# main.py (или app/main.py)
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

# Импортируем роутеры
from app.routers.players import router as players_router
from app.routers.sessions import router as sessions_router
from app.routers.characters import router as characters_router
from app.routers.items import router as items_router
from app.routers.abilities import router as abilities_router
from app.routers.maps import router as maps_router
from app.routers.map_objects import router as map_objects_router
from app.routers.npcs import router as npcs_router
from app.routers.effects import router as effects_router
from app.routers.event_templates import router as event_templates_router
from app.routers.inventory import router as inventory_router
from app.routers.event_instance import router as event_instance_router
from app.routers.theme import router as theme_router

# Подключаем движок и базу
from app.database import engine, Base

# Чтобы create_all увидел все модели, импортируем их
import app.models.player
import app.models.session
import app.models.character
import app.models.item
import app.models.ability
import app.models.map
import app.models.map_object
import app.models.npc
import app.models.effect
import app.models.event_template
import app.models.inventory
# import app.models.event_instance
import app.models.theme

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация базы данных (создание таблиц)
    print("Создаю таблицы...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы готовы.")
    yield

app = FastAPI(lifespan=lifespan)

# Регистрация роутеров
app.include_router(players_router)
app.include_router(sessions_router)
app.include_router(characters_router)
app.include_router(items_router)
app.include_router(abilities_router)
app.include_router(maps_router)
app.include_router(map_objects_router)
app.include_router(npcs_router)
app.include_router(effects_router)
app.include_router(event_templates_router)
app.include_router(inventory_router)
app.include_router(event_instance_router)
app.include_router(theme_router)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>D&D App</title>
        </head>
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
    Простая WebSocket-эндпоинт: принимает текстовые сообщения и отправляет обратно подтверждение.
    """
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Сообщение получено: {data}")