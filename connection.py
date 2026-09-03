
import os
import sqlite3



DBPATH = os.environ.get("DB_PATH", "/data/notes.db") 

def connect_to_db():
    try:
        conn = sqlite3.connect(DBPATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

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