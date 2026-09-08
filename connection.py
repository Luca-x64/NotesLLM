import os
import sqlite3
from fastapi import HTTPException,status

DBPATH = os.environ.get("DB_PATH", "/data/notes.db") 

def connect_to_db():
    try:
        conn = sqlite3.connect(DBPATH)
        return conn
    except sqlite3.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error":"Database Connection Error","message":f"Failed to connect to the database: {e}"})


def create_db():
    with connect_to_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (  
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            date DATE DEFAULT CURRENT_TIMESTAMP)
            """)
        conn.commit()

        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_note_date
            AFTER UPDATE ON notes
            FOR EACH ROW
            BEGIN
                UPDATE notes
                SET date = CURRENT_TIMESTAMP
                WHERE id = OLD.id;
            END;
        """)
        conn.commit()


def database_exception(e):
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail={
        "error": "Database Query Error",
        "message": f"Failed to execute database query: {e}"}
    )


def fetch_all(sql, params=()):
    try:
        with connect_to_db() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return cur.fetchall()
    except sqlite3.Error as e:
        raise database_exception(e)


def fetch_one(sql, params=()):
    try:
        with connect_to_db() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return cur.fetchone()
    except sqlite3.Error as e:
        raise database_exception(e)


def execute(sql, params=()):
    try:
        with connect_to_db() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return cur.rowcount
    except sqlite3.Error as e:
        raise database_exception(e)
