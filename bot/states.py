from aiogram.fsm.state import State, StatesGroup

class AuthStates(StatesGroup):
    waiting_for_code = State()

class BotMode(StatesGroup):
    dropbox = State()
    email = State()

class EmailStates(StatesGroup):
    waiting_for_email = State()
