import os
import dropbox
import io
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F, types
from dropbox import DropboxOAuth2FlowNoRedirect
from dotenv import load_dotenv
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import DB_PATH, SUPPORTED_BOOK_FORMATS
from validators import is_valid_book_format, is_valid_auth_code


load_dotenv()

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

class AuthStates(StatesGroup):
    waiting_for_code = State() 

def get_user_token(telegram_id: int) -> str | None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT dropbox_token, refresh_token, expires_at  
                       FROM dropbox_tokens WHERE telegram_id = ?
                       """, (telegram_id,))
        result = cursor.fetchone()
        return result if result else None

async def ensure_auth(message: types.Message, state: FSMContext) -> bool:
    print("Проверяем наличие токена")
    token_data = get_user_token(message.from_user.id)
    
    if not token_data:
        print("Токена нет, отправляем пользователя на авторизацию")
        await message.answer("Чтобы бот мог загружать книжки, нужно авторизоваться в Dropbox. Нажми /auth")
        return False

    access_token, refresh_token, expires_at  = token_data
    app_key = os.getenv("DROPBOX_APP_KEY")
    app_secret = os.getenv("DROPBOX_APP_SECRET")
    
    try:
        # Инициализация Dropbox клиента с рефреш-токеном
        dbx = dropbox.Dropbox(
            oauth2_access_token=access_token,
            oauth2_refresh_token=refresh_token,
            oauth2_access_token_expiration=datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S.%f"),
            app_key=app_key,
            app_secret=app_secret
        )
        
        # Проверка и обновление токена, если нужно
        dbx.check_and_refresh_access_token()

        # Получаем новый токен и дату истечения
        new_access_token = dbx._oauth2_access_token
        new_expires_at = dbx._oauth2_access_token_expiration.strftime("%Y-%m-%d %H:%M:%S.%f")

        # Сохраняем обновлённый токен в базу
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE dropbox_tokens
                SET dropbox_token = ?, expires_at = ?
                WHERE telegram_id = ?
            """, (new_access_token, new_expires_at, message.from_user.id))
            conn.commit()

        print(f"Токен обновлён и действителен, новое экспайр: {new_expires_at}")
        await state.update_data(dropbox_token=new_access_token)
        return True

    except Exception as e:
        print(f"Ошибка проверки или обновления токена: {e}")
        await message.answer("Не удалось проверить или обновить авторизацию в Dropbox. Попробуйте авторизоваться снова. Нажмите /auth")
        return False

async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("""
                         Привет! Чтоб авторизоваться в Dropbox нажми /auth
Если ты уже авторизовывался в Dropbox через меня, то можешь просто скинуть мне файл для загрузки или использовать другие команды (например /help)
                    """)

async def file_handler(message: types.Message, state: FSMContext, bot: Bot):
        if not await ensure_auth(message, state):
            return 

        file = message.document
        print(f"Получили файл {file.file_name}")

        if is_valid_book_format(file.file_name, SUPPORTED_BOOK_FORMATS):
            await message.answer(f"Вижу файл {file.file_name}, отправляем в Dropbox")

            file_in_io = io.BytesIO()
            file_info = await bot.get_file(file.file_id)
            dropbox_path = f"/Приложения/Dropbox PocketBook/{file.file_name}"
            await bot.download_file(file_info.file_path, file_in_io)

            data = await state.get_data()
            dropbox_token = data["dropbox_token"]

            with dropbox.Dropbox(oauth2_access_token=dropbox_token) as dbx:
                file_in_io.seek(0)
                dbx.files_upload(
                    file_in_io.read(), 
                    dropbox_path, 
                    mode=dropbox.files.WriteMode("overwrite")
                )

            await message.answer(f"Книга успешно загружена в Dropbox: {dropbox_path}")
            print(f"Книга успешно загружена в Dropbox: {dropbox_path}")
        else:
            await message.answer("Это не электронная книга. Отправьте файл в подходящем формате")
            print(f'Неверный формат книги {file.file_name}')


APP_KEY = os.getenv("DROPBOX_APP_KEY")
APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
auth_flow = DropboxOAuth2FlowNoRedirect(
    consumer_key=APP_KEY,
    consumer_secret=APP_SECRET,
    token_access_type="offline"
)

async def auth_handler(message: types.Message, state: FSMContext):
    auth_url = auth_flow.start()
    await message.answer(f"""Для авторизации перейдите по ссылке: {auth_url}
После авторизации скопируйте код и отправьте его мне""")
    await state.set_state(AuthStates.waiting_for_code)

async def process_auth_code(message: types.Message, state: FSMContext):
    auth_code = message.text.strip()

    try:
        oauth_result = auth_flow.finish(auth_code)
        access_token = oauth_result.access_token
        refresh_token = oauth_result.refresh_token
        expires_at = oauth_result.expires_at

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dropbox_tokens (telegram_id, dropbox_token, refresh_token, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE 
                SET dropbox_token = excluded.dropbox_token,
                    refresh_token = excluded.refresh_token,
                    expires_at = excluded.expires_at
            """, (message.from_user.id, access_token, refresh_token, expires_at))
            conn.commit()

        with dropbox.Dropbox(oauth2_access_token=access_token) as dbx:
            user_account = dbx.users_get_current_account()
            print(f"Successfully set up client for {user_account.name.display_name}!")
            await message.answer("Авторизация прошла успешно!")

    except Exception as e:
        await message.answer(f"Произошла ошибка при авторизации: {e}")
    finally:
        await state.clear()

def register_handlers(dp: Dispatcher):
    dp.message.register(start, F.text == "/start")
    dp.message.register(auth_handler, F.text == "/auth")
    dp.message.register(file_handler, F.document)
    dp.message.register(process_auth_code, AuthStates.waiting_for_code)
    