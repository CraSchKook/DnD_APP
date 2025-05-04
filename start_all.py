import subprocess
import time
import requests
import os
from dotenv import load_dotenv
import os

load_dotenv()
PROJECT_DIR = os.getenv("PROJECT_DIR")
NGROK_PATH = os.getenv("NGROK_PATH")

VENV_PYTHON = os.path.join(PROJECT_DIR, ".venv", "Scripts", "python.exe")


def get_ngrok_url():
    try:
        resp = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = resp.json()
        for tunnel in data["tunnels"]:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
        return data["tunnels"][0]["public_url"]
    except Exception:
        return None

# 1. Запускаем FastAPI (без --reload)
fastapi_proc = subprocess.Popen(
    [VENV_PYTHON, "-m", "uvicorn", "app.main:app"],
    cwd=PROJECT_DIR
)
print("FastAPI сервер запущен.")

time.sleep(5)

# 2. Запускаем ngrok
ngrok_proc = subprocess.Popen(
    [NGROK_PATH, "http", "8000"],
    cwd=os.path.dirname(NGROK_PATH)
)
print("ngrok запущен.")

# 3. Ждём, чтобы ngrok успел подняться и получить ссылку
ngrok_url = None
for _ in range(20):  # 20 попыток по 1 сек = 20 секунд ожидания
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        break
    time.sleep(1)

if ngrok_url:
    print("\nВАША ПУБЛИЧНАЯ ССЫЛКА NGROK:")
    print(ngrok_url)
    print("\nОтправьте её друзьям или используйте для Telegram-бота.")
else:
    print("❌ Не удалось получить публичный URL от ngrok. Проверьте, что ngrok запустился корректно.")

# 4. Запускаем Telegram-бота
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
    for proc, name in [(bot_proc, "Бот"), (fastapi_proc, "FastAPI"), (ngrok_proc, "ngrok")]:
        if proc.poll() is None:
            print(f"Завершение процесса {name}...")
            # Для Windows используем .terminate(), для Linux/Mac можно использовать .send_signal(signal.SIGINT)
            proc.terminate()
    print("Все процессы остановлены.")
