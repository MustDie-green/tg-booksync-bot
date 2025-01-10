from dotenv import load_dotenv
import os

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")

SUPPORTED_BOOK_FORMATS = {".epub", ".fb2", ".pdf", ".mobi"}
DB_PATH = "dropbox_tokens.db"
