#!/usr/bin/env python3
import time
import json
import hmac
import hashlib
import urllib.parse
import secrets
import os

# Подставьте сюда ваш настоящий BOT_TOKEN
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7458761191:AAHAB3L1_Dx7nMjyHpHquotnjhZi3v1sovY")

def generate_init_data(user_info: dict) -> str:
    """
    Генерирует initData точно по алгоритму FastAPI-функции verify_telegram_hash:
    1) raw_params с неэкранированным JSON
    2) data_check_string = "\n".join(sorted(key=value из raw_params))
    3) HMAC-SHA256 по secret_key = SHA256(BOT_TOKEN)
    4) GET-параметры: те же поля, но user — URL-encoded
    """
    # --- 1. Собираем «сырые» параметры ---
    raw_params = {
        "query_id" : secrets.token_urlsafe(16),
        # user — НЕЭКРАНИРОВАННЫЙ JSON со всеми русскими буквами
        "user"     : json.dumps(user_info, separators=(",", ":"), ensure_ascii=False),
        "auth_date": str(int(time.time())),  # UNIX timestamp UTC
    }

    # --- 2. Собираем data_check_string по сортированным ключам ---
    data_check_list = [f"{k}={raw_params[k]}" for k in sorted(raw_params.keys())]
    data_check_string = "\n".join(data_check_list).encode("utf-8")

    # --- 3. Считаем HMAC-SHA256 ---
    secret_key = hashlib.sha256(BOT_TOKEN.encode("utf-8")).digest()
    calculated_hash = hmac.new(secret_key, data_check_string, hashlib.sha256).hexdigest()

    # --- 4. Кодируем в URL ---
    url_params = {
        "query_id" : raw_params["query_id"],
        # URL-кодируем JSON-поле
        "user"     : urllib.parse.quote(raw_params["user"], safe=""),
        "auth_date": raw_params["auth_date"],
        "hash"     : calculated_hash
    }
    # порядок полей в строке не имеет значения
    return "&".join(f"{k}={url_params[k]}" for k in url_params)

if __name__ == "__main__":
    user = {
        "id": 7424978915,
        "first_name": "Дали",
        "last_name": "",
        "username": "dddalia",
        "language_code": "ru",
        "allows_write_to_pm": True,
        "photo_url": "https://t.me/i/userpic/320/iaAzb6Eg6MHhJtti8bD-Y8BxdS_AymAi4PQntPpp8dxbdqidqmHbKYYmi1B-GyK3.svg"
    }

    init_data = generate_init_data(user)
    print("Сгенерированная initData:\n")
    print(init_data)



"""
import os, hmac, hashlib

BOT_TOKEN = os.getenv("BOT_TOKEN")  # возьмёт из вашего .env
# Эти поля мы хотим подать:
params = {
    "id": "123446789",
    "first_name": "mister",
    "username": "propper",
    "auth_date": "1700000000"
}

# 1) Собираем check_string (лексикографически отсортированные key=value)
data_check_arr = []
for key in sorted(params.keys()):
    data_check_arr.append(f"{key}={params[key]}")
check_string = "\n".join(data_check_arr).encode("utf-8")

# 2) Секретный ключ для HMAC = SHA256(bot_token)
secret_key = hashlib.sha256(BOT_TOKEN.encode("utf-8")).digest()

# 3) Считаем HMAC-SHA256
hmac_obj = hmac.new(secret_key, check_string, hashlib.sha256)
calculated_hash = hmac_obj.hexdigest()

# 4) Формируем итоговую строку initData
parts = []
for k, v in params.items():
    parts.append(f"{k}={v}")
parts.append(f"hash={calculated_hash}")
init_data = "&".join(parts)
print(init_data)
"""