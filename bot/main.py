import asyncio
from aiogram import Bot, Dispatcher
from config import TELEGRAM_BOT_TOKEN
from handlers import register_handlers, init_db
import os

if not os.path.exists("temp"):
    os.makedirs("temp")

async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    
    register_handlers(dp)
    
    print('Запускаем бота')
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    init_db() 
    asyncio.run(main())