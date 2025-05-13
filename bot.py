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

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer(
        "Привет! Это ваше Mini App 👇",
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
            types.KeyboardButton(text="Открыть приложение")
        )
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
