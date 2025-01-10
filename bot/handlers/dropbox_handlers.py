import os
import logging
import io
import dropbox
from datetime import datetime

from dropbox import DropboxOAuth2FlowNoRedirect
from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.services.db_services import get_user_token, save_user_token, update_access_token

from config import DROPBOX_APP_KEY, DROPBOX_APP_SECRET, SUPPORTED_BOOK_FORMATS


class AuthStates(StatesGroup):
    waiting_for_code = State()


async def auth_handler(message: types.Message, state: FSMContext):
    await state.clear()
    auth_flow = DropboxOAuth2FlowNoRedirect(
        consumer_key=DROPBOX_APP_KEY,
        consumer_secret=DROPBOX_APP_SECRET,
        token_access_type="offline"
    )

    await state.update_data(auth_flow=auth_flow)

    auth_url = auth_flow.start()
    await message.answer(
        f"Для авторизации перейдите по ссылке: {auth_url}\n"
        "После авторизации скопируйте код и отправьте его мне."
    )

    await state.set_state(AuthStates.waiting_for_code)


async def process_auth_code(message: types.Message, state: FSMContext):
    data = await state.get_data()
    auth_flow: DropboxOAuth2FlowNoRedirect = data.get("auth_flow")
    if not auth_flow:
        logging.error("Ошибка: Не удалось найти auth_flow. Попробуйте ещё раз /auth")
        await state.clear()
        return

    auth_code = message.text.strip()

    try:
        oauth_result = auth_flow.finish(auth_code)
        access_token = oauth_result.access_token
        refresh_token = oauth_result.refresh_token
        expires_at = oauth_result.expires_at 

        save_user_token(
            telegram_id=message.from_user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at
        )

        with dropbox.Dropbox(oauth2_access_token=access_token) as dbx:
            user_account = dbx.users_get_current_account()
            await message.answer(
                f"Авторизация прошла успешно!"
            )
            logging.info(f"Авторизация прошла успешно для {user_account.name.display_name}!")

    except Exception as e:
        await message.answer(f"Произошла ошибка при авторизации, попробуйте еще раз или напишите автору бота")
        logging.error(f'Ошибка при авторизации: {e}')
    finally:
        await state.clear()



async def ensure_auth(message: types.Message, state: FSMContext) -> bool:
    token_data = get_user_token(message.from_user.id)
    if not token_data:
        await message.answer(
            "Чтобы загружать книжки, нужно авторизоваться в Dropbox.\n"
            "Нажмите /auth"
        )
        return False

    access_token, refresh_token, expires_at_str = token_data
    try:
        dbx = dropbox.Dropbox(
            oauth2_access_token=access_token,
            oauth2_refresh_token=refresh_token,
            oauth2_access_token_expiration=datetime.strptime(
                expires_at_str, "%Y-%m-%d %H:%M:%S.%f"
            ),
            app_key=DROPBOX_APP_KEY,
            app_secret=DROPBOX_APP_SECRET,
        )
        dbx.check_and_refresh_access_token()

        new_access_token = dbx._oauth2_access_token
        new_expires_at = dbx._oauth2_access_token_expiration.strftime("%Y-%m-%d %H:%M:%S.%f")

        if new_access_token != access_token:
            update_access_token(message.from_user.id, new_access_token, new_expires_at)

        await state.update_data(dropbox_token=new_access_token)
        return True

    except Exception as e:
        await message.answer(
            "Не удалось проверить или обновить авторизацию. Попробуйте авторизоваться заново — /auth."
        )
        logging.error(f'Ошибка рефреша токена: {e}')
        return False



async def file_handler(message: types.Message, state: FSMContext):
    if not await ensure_auth(message, state):
        return

    file = message.document
    if not file:
        message.answer("Похоже, что это не документ :)")
        logging.warning('Не нашли файл в сообщении')
        return

    file_name = file.file_name or ""
    _, ext = os.path.splitext(file_name)
    if ext.lower() not in SUPPORTED_BOOK_FORMATS:
        await message.answer(f"Похоже, это не электронная книга. Отправьте .epub, .pdf, fb2 или .mobi\n"
                             "Если вы хотите, чтобы под поддерживал больше форматов, напишите автору бота или сделайте pull request — /help")
        logging.warning(f'Прислали файл неподходящего формата: {file_name}')
        return

    await message.answer(f"Получил файл {file_name}, отправляем в Dropbox.")

    file_in_io = io.BytesIO()
    file_info = await message.bot.get_file(file.file_id)
    await message.bot.download_file(file_info.file_path, file_in_io)

    dropbox_path = f"/Приложения/Dropbox PocketBook/{file_name}"
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


def register_dropbox_handlers(dp: Dispatcher):
    dp.message.register(auth_handler, F.text == "/auth")
    dp.message.register(process_auth_code, AuthStates.waiting_for_code)

    dp.message.register(file_handler, F.document)