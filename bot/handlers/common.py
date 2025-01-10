from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext

async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("""
Привет! Я бот для загрузки электронных книжек на читалку Pocketbook через Dropbox
Для этого тебе надо авторизоваться в Dropbox через /auth, а потом скинуть мне файл с книжкой и я загружу его в твой Dropbox в папку, с которой синхронизируется Pocketbook
Чтобы узнать больше подробностей — /help
""")

async def cmd_help(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("""
Список команд:
/auth - Авторизация
/start - Начало
                         
Как работает бот:
1. Сначала вы нажимаете /auth — бот кидает вам ссылку для авторизации в Dropbox, переходите по ней, получаете одноразовый ключ и скидываете боту
По этому ключу бот получает доступ ТОЛЬКО НА ЗАПИСЬ — он не сможет украсть ваши файлы, даже если захочет
Если что, отозвать доступ можно тут — https://www.dropbox.com/account/connected_apps 
(Важно — доступы, которые написаны там, не соответствуют действительности, реальные доступы, которые запрашивает бот, можно увидеть по ссылке из /auth)
2. Когда бот сказал, что авторизация прошла успешно, вы можете скидывать ему файлы .epub, .mobi, .pdf, .fb2 и он зальет их в ваш Dropbox в папку /Приложения/Dropbox PocketBook/
Важно — перед тем, как пользоваться этим ботом, нужно зайти в Dropbox на вашей читалке Pocketbook, чтобы появилась эта папка и чтобы читалка подхватывала файлы оттуда
                         
Разработчик бота — https://github.com/MustDie-green
Вопросы и предложения в телегу — @mustdie_green
Исходный код — https://github.com/MustDie-green/tg-booksync-bot (туда же можно кидать issue и пулл реквесты)
""")

def register_common_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, F.text == "/start")
    dp.message.register(cmd_help, F.text == "/help")