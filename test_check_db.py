import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()

cursor.execute("PRAGMA database_list;")
print("Открытые базы:", cursor.fetchall())

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Таблицы:", cursor.fetchall())

cursor.execute("SELECT * FROM players;")
print("Игроки:", cursor.fetchall())

conn.close()
