from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sqlite3

app = FastAPI(title="ToDo Service")

DB_PATH = "data/todo.db"


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN NOT NULL
        )
    """)
    conn.commit()
    conn.close()


create_table()


class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class Item(ItemCreate):
    id: int


@app.post("/items", response_model=Item)
def create_item(item: ItemCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO items (title, description, completed) VALUES (?, ?, ?)",
        (item.title, item.description, item.completed)
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return {**item.dict(), "id": item_id}


@app.get("/items", response_model=List[Item])
def get_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed FROM items")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "title": r[1],
            "description": r[2],
            "completed": bool(r[3])
        }
        for r in rows
    ]


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, description, completed FROM items WHERE id=?",
        (item_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Item not found")

    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "completed": bool(row[3])
    }


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE items
        SET title=?, description=?, completed=?
        WHERE id=?
    """, (item.title, item.description, item.completed, item_id))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")

    conn.commit()
    conn.close()
    return {**item.dict(), "id": item_id}


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")

    conn.commit()
    conn.close()
    return {"status": "deleted"}
