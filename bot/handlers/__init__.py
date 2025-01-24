from aiogram import Dispatcher
from .common import register_common_handlers
from .file_handler import register_file_handler
from .user_data_handlers import register_user_data_handlers

def register_all_handlers(dp: Dispatcher):
    register_common_handlers(dp)
    register_user_data_handlers(dp)
    register_file_handler(dp)