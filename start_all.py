import subprocess
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()
PROJECT_DIR = os.getenv("PROJECT_DIR")

VENV_PYTHON = os.path.join(PROJECT_DIR, ".venv", "Scripts", "python.exe")

# 1. Запускаем FastAPI (без --reload)
fastapi_proc = subprocess.Popen(
    [VENV_PYTHON, "-m", "uvicorn", "app.main:app"],
    cwd=PROJECT_DIR
)
print("FastAPI сервер запущен.")

time.sleep(5)

# 2. Запускаем Telegram-бота
bot_proc = subprocess.Popen(
    [VENV_PYTHON, "bot.py"],
    cwd=PROJECT_DIR
)
print("Telegram-бот запущен.\n")

print("Для остановки всех процессов нажмите Ctrl+C или закройте окно.")

try:
    bot_proc.wait()
except KeyboardInterrupt:
    print("\nОстановка всех процессов...")
finally:
    for proc, name in [(bot_proc, "Бот"), (fastapi_proc, "FastAPI")]:
        if proc.poll() is None:
            print(f"Завершение процесса {name}...")
            # Для Windows используем .terminate(), для Linux/Mac можно использовать .send_signal(signal.SIGINT)
            proc.terminate()
    print("Все процессы остановлены.")
