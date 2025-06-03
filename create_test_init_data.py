# file: create_test_init_data.py
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
