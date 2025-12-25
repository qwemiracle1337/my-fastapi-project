from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import sqlite3
import string
import random
from pathlib import Path

# Путь к базе
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "shorturl.db"

app = FastAPI(title="Short URL Service")

# Подключение к SQLite
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# Создаём таблицу при запуске
def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            short_id TEXT PRIMARY KEY,
            full_url TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Событие запуска приложения
@app.on_event("startup")
def startup():
    # Создаём папку data, если её нет
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    create_table()

# Pydantic модели
class URLCreate(BaseModel):
    url: HttpUrl

class URLInfo(BaseModel):
    short_id: str
    full_url: HttpUrl

# Генератор короткого ID
def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# POST /shorten — создание короткой ссылки
@app.post("/shorten", response_model=URLInfo)
def shorten_url(url: URLCreate):
    conn = get_connection()
    cursor = conn.cursor()

    # Генерируем уникальный short_id
    while True:
        short_id = generate_short_id()
        cursor.execute("SELECT 1 FROM urls WHERE short_id=?", (short_id,))
        if not cursor.fetchone():
            break

    cursor.execute(
    "INSERT INTO urls (short_id, full_url) VALUES (?, ?)", 
    (short_id, str(url.url))  # <- преобразуем в строку
)
    conn.commit()
    conn.close()
    return {"short_id": short_id, "full_url": url.url}

# GET /{short_id} — редирект (для Swagger возвращаем JSON)
@app.get("/{short_id}")
def redirect_url(short_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_url FROM urls WHERE short_id=?", (short_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return {"redirect_to": row[0]}

# GET /stats/{short_id} — информация о ссылке
@app.get("/stats/{short_id}", response_model=URLInfo)
def stats(short_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_url FROM urls WHERE short_id=?", (short_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return {"short_id": short_id, "full_url": row[0]}
