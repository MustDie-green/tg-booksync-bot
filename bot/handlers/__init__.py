from aiogram import Dispatcher
from .dropbox_handlers import register_dropbox_handlers
from .common import register_common_handlers

def register_all_handlers(dp: Dispatcher):
    register_common_handlers(dp)
    register_dropbox_handlers(dp)