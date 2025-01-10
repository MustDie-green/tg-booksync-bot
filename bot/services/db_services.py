import sqlite3
from config import DB_PATH

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dropbox_tokens (
                telegram_id INTEGER PRIMARY KEY,
                dropbox_token TEXT NOT NULL,
                refresh_token TEXT NOT NULL, 
                expires_at DATETIME NOT NULL
            )
        """)
        conn.commit()

def get_user_token(telegram_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT dropbox_token, refresh_token, expires_at 
            FROM dropbox_tokens
            WHERE telegram_id = ?
        """, (telegram_id,))
        return cursor.fetchone()

def save_user_token(telegram_id: int, access_token: str, refresh_token: str, expires_at):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dropbox_tokens (telegram_id, dropbox_token, refresh_token, expires_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE
            SET dropbox_token = excluded.dropbox_token,
                refresh_token = excluded.refresh_token,
                expires_at = excluded.expires_at
        """, (telegram_id, access_token, refresh_token, str(expires_at)))
        conn.commit()

def update_access_token(telegram_id: int, new_access_token: str, new_expires_at: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dropbox_tokens
            SET dropbox_token = ?, expires_at = ?
            WHERE telegram_id = ?
        """, (new_access_token, new_expires_at, telegram_id))
        conn.commit()