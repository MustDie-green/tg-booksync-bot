from dotenv import load_dotenv
import os

SUPPORTED_BOOK_FORMATS = {".epub", ".fb2", ".pdf", ".mobi"}
EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

DB_PATH = "dropbox_tokens.db"

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
YANDEX_LOGIN = os.getenv("YANDEX_LOGIN")
YANDEX_PASSWORD = os.getenv("YANDEX_PASSWORD")