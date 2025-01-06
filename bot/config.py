from dotenv import load_dotenv
import os

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUPPORTED_BOOK_FORMATS = {".epub", ".fb2", ".pdf", ".mobi"}
DB_PATH = "dropbox_tokens.db" 

