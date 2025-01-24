import logging
import io
import dropbox
from datetime import datetime

from aiogram import types
from aiogram.fsm.context import FSMContext

from bot.services.db_services import (
    update_user_data,
    get_user_data,
)

from config import (
    DROPBOX_APP_KEY,
    DROPBOX_APP_SECRET
)

async def ensure_dropbox_auth(message: types.Message, state: FSMContext) -> bool:
    token_data = get_user_data(message.from_user.id)
    if not token_data:
        await message.answer(
            "Чтобы загружать книжки, нужно авторизоваться в Dropbox.\n"
            "Нажмите /auth"
        )
        return False

    dropbox_token, refresh_token, expires_at_str, user_email = token_data
    if not dropbox_token:
        await message.answer("Похоже, вы не получали токен Dropbox. Нажмите /auth, чтобы авторизоваться.")
        return False

    try:
        dbx = dropbox.Dropbox(
            oauth2_access_token=dropbox_token,
            oauth2_refresh_token=refresh_token,
            oauth2_access_token_expiration=datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S.%f"),
            app_key=DROPBOX_APP_KEY,
            app_secret=DROPBOX_APP_SECRET,
        )
        dbx.check_and_refresh_access_token()

        new_access_token = dbx._oauth2_access_token
        new_expires_at = dbx._oauth2_access_token_expiration.strftime("%Y-%m-%d %H:%M:%S.%f")

        if new_access_token != dropbox_token:
            update_user_data(
                telegram_id=message.from_user.id,
                dropbox_token=new_access_token,
                expires_at=new_expires_at
            )

        await state.update_data(dropbox_token=new_access_token)
        return True

    except Exception as e:
        await message.answer("Не удалось проверить или обновить авторизацию. Попробуйте авторизоваться заново /auth.")
        logging.error(f"Ошибка рефреша токена: {e}")
        return False


async def upload_book_to_dropbox(file_in_io: io.BytesIO, file_name: str, state: FSMContext):
    data = await state.get_data()
    dropbox_token = data.get("dropbox_token")
    if not dropbox_token:
        raise ValueError("Dropbox token not found in FSM state.")

    dropbox_path = f"/Приложения/Dropbox PocketBook/{file_name}"
    with dropbox.Dropbox(oauth2_access_token=dropbox_token) as dbx:
        file_in_io.seek(0)
        dbx.files_upload(
            file_in_io.read(),
            dropbox_path,
            mode=dropbox.files.WriteMode("overwrite")
        )
