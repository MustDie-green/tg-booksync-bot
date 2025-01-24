from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from bot.states import BotMode

from config import SUPPORTED_BOOK_FORMATS

async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("""
Привет! Я бот для загрузки электронных книжек на читалку через почту для синхронизации или через Dropbox (только Pocketbook).
/auth_dropbox — добавить Dropbox
/add_email — добавить почту
А потом можешь просто отправлять мне книжки файлом!
                         
Если хочешь поменять режим Dropbox или почта, есть /set_dropbox и /set_email
Список команд — /help
""")

async def cmd_help(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("""
Список команд:
/start — Начало
/help — Список команд
/auth_dropbox — Авторизация в Dropbox
/set_dropbox — Режим отправки книжек в дропбокс
/add_email — Добавить почту для отправки книжек
/set_email — Режим отправки книжек на почту
                         
Про работу бота подробнее и контакты автора — /big_help
""")
    
async def cmd_big_help(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(f"""
Доступные форматы: {', '.join(SUPPORTED_BOOK_FORMATS)}
Если хотите добавить еще — напишите автору бота или сделайте пулл реквест (см нижнюю часть сообщения)

Как работает через Dropbox:
0. Чтобы пользоваться этим способом, нужно зайти в Dropbox на вашей читалке Pocketbook, чтобы появилась папка `/Приложения/Dropbox PocketBook/` и чтобы читалка подхватывала файлы оттуда, — бот будет класть книжки туда.
Из-за того, что бот грузит в папку Dropbox PocketBook, этот способ работает только с читалками Pocketbook.
1. Сначала вы нажимаете /auth — бот кидает вам ссылку для авторизации в Dropbox, переходите по ней, получаете одноразовый ключ и скидываете боту.
По этому ключу бот получает доступ ТОЛЬКО НА ЗАПИСЬ — он не сможет украсть ваши файлы, даже если захочет.
Если что, отозвать доступ можно тут — https://www.dropbox.com/account/connected_apps 
(Важно — там написаны неправильные доступы. Реальные доступы бота можно увидеть по ссылке из /auth)
2. Когда бот сказал, что авторизация прошла успешно, вы можете скидывать ему книжки файлом или пересылом.

Как работает через почту:
0. Сначала нужно получить для своей читалки почту для синхронизации, у Pocketbook это будет почта с @pbsync.com.
Этот способ работает для любых читалок, которые умеют получать книжки на почту.
+ он более безопасный, тк вы не даете доступ к своему Dropbox.
2. После этого жмем /add_email и отправляем эту почту боту — бот ее сохранит.
3. Все, можно просто отправлять боту книжки файлом или пересылом сообщения.
                         
Разработчик бота — https://github.com/MustDie-green
Вопросы, проблемы и предложения в телегу — @mustdie_green
Исходный код — https://github.com/MustDie-green/tg-booksync-bot (туда же можно кидать issue и пулл реквесты)
""")
    
async def set_dropbox_mode(message: types.Message, state: FSMContext):
    await state.set_state(BotMode.dropbox)
    await message.answer("Теперь бот будет загружать файлы в Dropbox.")

async def set_email_mode(message: types.Message, state: FSMContext):
    await state.set_state(BotMode.email)
    await message.answer("Теперь бот будет отправлять файлы на почту.")

def register_common_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, F.text == "/start")
    dp.message.register(cmd_help, F.text == "/help")
    dp.message.register(cmd_big_help, F.text == "/big_help")
    
    dp.message.register(set_dropbox_mode, F.text == "/set_dropbox")
    dp.message.register(set_email_mode, F.text == "/set_email")