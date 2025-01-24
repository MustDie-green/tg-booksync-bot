import os
import logging
import io

from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext

from bot.services.mail_services import send_book_via_yandex

from bot.services.db_services import get_user_data
from bot.states import BotMode
from bot.services.dropbox_services import ensure_dropbox_auth, upload_book_to_dropbox

from config import SUPPORTED_BOOK_FORMATS

async def file_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    file = message.document
    if not file:
        logging.warning("Не найден файл в сообщении")
        await message.answer("Похоже, это не документ. Пришлите файл заново.")
        return

    file_name = file.file_name or ""
    _, ext = os.path.splitext(file_name)
    if ext.lower() not in SUPPORTED_BOOK_FORMATS:
        await message.answer(f"Похоже, это не электронная книга. Отправьте {', '.join(SUPPORTED_BOOK_FORMATS)}\n"
                             "Если вы хотите, чтобы под поддерживал больше форматов, напишите автору бота или сделайте pull request — /help")
        logging.warning(f"Прислали файл неподходящего формата: {file_name}")
        return

    file_in_io = io.BytesIO()
    file_info = await message.bot.get_file(file.file_id)
    await message.bot.download_file(file_info.file_path, file_in_io)

    if current_state == BotMode.dropbox.state:
        if not await ensure_dropbox_auth(message, state):
            message.answer('Включен режим Dropbox, но вы не авторизировались в нем, нажмите /auth')
            return
        await message.answer(f"Получил файл {file_name}, отправляем в Dropbox.")
        await upload_book_to_dropbox(file_in_io, file_name, state)
        await message.answer(f"Книга успешно загружена в Dropbox: /Приложения/Dropbox PocketBook/{file_name}")

    elif current_state == BotMode.email.state:
        user_data = get_user_data(message.from_user.id)
        if not user_data:
            await message.answer("Вы не добавили почту. Нажмите /add_email.")
            return

        dropbox_token, refresh_token, expires_at, user_email = user_data
        if not user_email:
            await message.answer("Вы не добавили почту. Нажмите /add_email.")
            return
        await message.answer(f"Получил файл {file_name}, отправляем на почту {user_email}")

        file_in_io.seek(0)
        try:
            send_book_via_yandex(
                to_email=user_email,
                subject="Book from flexbooksync",
                text_body="Your book from flexbooksync",
                file_bytes=file_in_io.read(),
                file_name=file_name
            )
            await message.answer(f"Книга {file_name} отправлена на {user_email}!")
        except Exception as e:
            await message.answer(f"Произошла ошибка при отправке на почту: {e}")

    else:
        await message.answer("Сначала выберите режим работы: /set_dropbox или /set_email.")

def register_file_handler(dp: Dispatcher):
    dp.message.register(file_handler, F.document)
