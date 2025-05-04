from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from app.routers import players
from app.routers import sessions
from app.routers import characters
from app.routers import items
from app.routers import abilities
from app.routers import maps
from app.routers import map_objects
from app.routers import npcs
from app.routers import effects
from app.routers import event_templates
from app.routers import inventory
from app.routers import event_instance
from app.routers import theme

app = FastAPI()

# 👇 подключаем роутер
app.include_router(players.router)
app.include_router(sessions.router)
app.include_router(characters.router)
app.include_router(items.router)
app.include_router(abilities.router)
app.include_router(maps.router)
app.include_router(map_objects.router)
app.include_router(npcs.router)
app.include_router(effects.router)
app.include_router(event_templates.router)
app.include_router(inventory.router)
app.include_router(event_instance.router)
app.include_router(theme.router)

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
                const ws = new WebSocket("wss://" + location.host + "/ws");

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
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Сообщение получено: {data}")