from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import sqlite3
import string
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "shorturl.db"

app = FastAPI(title="Short URL Service")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

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

@app.on_event("startup")
def startup():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    create_table()

class URLCreate(BaseModel):
    url: HttpUrl

class URLInfo(BaseModel):
    short_id: str
    full_url: HttpUrl

def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.post("/shorten", response_model=URLInfo)
def shorten_url(url: URLCreate):
    conn = get_connection()
    cursor = conn.cursor()

    while True:
        short_id = generate_short_id()
        cursor.execute("SELECT 1 FROM urls WHERE short_id=?", (short_id,))
        if not cursor.fetchone():
            break

    cursor.execute(
    "INSERT INTO urls (short_id, full_url) VALUES (?, ?)", 
    (short_id, str(url.url))  
)
    conn.commit()
    conn.close()
    return {"short_id": short_id, "full_url": url.url}

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
