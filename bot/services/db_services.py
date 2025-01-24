import sqlite3
from config import DB_PATH

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                telegram_id INTEGER PRIMARY KEY,
                dropbox_token TEXT,
                refresh_token TEXT,
                expires_at TEXT,
                email TEXT
            )
        """)
        conn.commit()

def get_user_data(telegram_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT dropbox_token, refresh_token, expires_at, email
            FROM user_data
            WHERE telegram_id = ?
        """, (telegram_id,))
        return cursor.fetchone()

def update_user_data(telegram_id: int, dropbox_token=None, refresh_token=None, expires_at=None, email=None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        fields = []
        params = []

        if dropbox_token is not None:
            fields.append("dropbox_token = ?")
            params.append(dropbox_token)
        if refresh_token is not None:
            fields.append("refresh_token = ?")
            params.append(refresh_token)
        if expires_at is not None:
            fields.append("expires_at = ?")
            params.append(expires_at)
        if email is not None:
            fields.append("email = ?")
            params.append(email)

        if not fields:
            return

        set_clause = ", ".join(fields)
        params.append(telegram_id)

        cursor.execute(f"""
            INSERT INTO user_data (telegram_id) VALUES (?)
            ON CONFLICT(telegram_id) DO NOTHING
        """, (telegram_id,))

        cursor.execute(f"""
            UPDATE user_data
            SET {set_clause}
            WHERE telegram_id = ?
        """, tuple(params))

        conn.commit()