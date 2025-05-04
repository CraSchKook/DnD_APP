import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from dotenv import load_dotenv
import os

# токен от BotFather
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_ngrok_url() -> str:
    """Достаём публичный URL из локального API ngrok."""
    try:
        resp = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = resp.json()
        # Предпочтительно HTTPS
        for tunnel in data["tunnels"]:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
        # Если HTTPS нет, берём первый попавшийся
        return data["tunnels"][0]["public_url"]
    except Exception as e:
        print("Не удалось получить URL ngrok:", e)
        return ""

@dp.message(F.text == "/start")
async def start(message: types.Message):
    url = get_ngrok_url()
    if not url:
        await message.reply("❌ Ngrok не запущен или не отвечает.")
        return

    web_app_button = types.KeyboardButton(
        text="Открыть приложение",
        web_app=types.WebAppInfo(url=url)
    )
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(web_app_button)

    await message.answer(
        "Привет! Нажми кнопку, чтобы открыть наше Mini App 👇",
        reply_markup=keyboard
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
