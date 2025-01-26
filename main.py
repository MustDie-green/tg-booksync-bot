import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TELEGRAM_BOT_TOKEN  
from bot.handlers import register_all_handlers 
from bot.services.db_services import init_db
from aiohttp import ClientSession, ClientTimeout

logging.basicConfig(level=logging.DEBUG)

async def main():
    init_db()

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    
    register_all_handlers(dp)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())