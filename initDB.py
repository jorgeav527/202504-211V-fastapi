import sqlite3


def init_db():
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS post (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            comment TEXT,
            createdAt TEXT,
            updatedAt TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()