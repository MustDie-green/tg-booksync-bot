import logging
import re
import dropbox

from dropbox import DropboxOAuth2FlowNoRedirect
from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext

from bot.states import AuthStates, EmailStates, BotMode

from bot.services.db_services import update_user_data

from bot.validators import is_valid_email

from config import (
    DROPBOX_APP_KEY,
    DROPBOX_APP_SECRET
)

async def add_email(message: types.Message, state: FSMContext):
    await message.answer("Введите вашу электронную почту для отправки книжек:")
    await state.set_state(EmailStates.waiting_for_email)

async def process_email(message: types.Message, state: FSMContext):
    email_candidate = message.text.strip()
    if not is_valid_email(email_candidate):
        await message.answer("Это не похоже на электронную почту. Попробуйте снова /add_email.")
        await state.clear()
        return
    
    update_user_data(
        telegram_id=message.from_user.id,
        email=email_candidate
    )

    await message.answer(f"Электронная почта {email_candidate} сохранена, теперь можно отправлять мне книжки!")
    await state.clear()
    await state.set_state(BotMode.email)

async def dropbox_auth_handler(message: types.Message, state: FSMContext):
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

async def process_dropbox_auth_code(message: types.Message, state: FSMContext):
    data = await state.get_data()
    auth_flow: DropboxOAuth2FlowNoRedirect = data.get("auth_flow")
    if not auth_flow:
        logging.error("Ошибка: Не удалось найти auth_flow. Попробуйте ещё раз /auth.")
        await state.clear()
        return

    auth_code = message.text.strip()

    try:
        oauth_result = auth_flow.finish(auth_code)
        access_token = oauth_result.access_token
        refresh_token = oauth_result.refresh_token
        expires_at = oauth_result.expires_at 

        update_user_data(
            telegram_id=message.from_user.id,
            dropbox_token=access_token,
            refresh_token=refresh_token,
            expires_at=str(expires_at)
        )

        with dropbox.Dropbox(oauth2_access_token=access_token) as dbx:
            user_account = dbx.users_get_current_account()
            await message.answer("Авторизация прошла успешно! Теперь можно отправлять мне книжки")
            logging.info(f"Авторизация прошла успешно для {user_account.name.display_name}!")

    except Exception as e:
        await message.answer("Произошла ошибка при авторизации. Попробуйте ещё раз или напишите автору бота.")
        logging.error(f"Ошибка при авторизации: {e}")
    finally:
        await state.clear()
        await state.set_state(BotMode.dropbox)

def register_user_data_handlers(dp: Dispatcher):
    dp.message.register(process_dropbox_auth_code, AuthStates.waiting_for_code)
    dp.message.register(dropbox_auth_handler, F.text == "/auth_dropbox")
    dp.message.register(process_dropbox_auth_code, AuthStates.waiting_for_code)

    dp.message.register(add_email, F.text == "/add_email")
    dp.message.register(process_email, EmailStates.waiting_for_email)