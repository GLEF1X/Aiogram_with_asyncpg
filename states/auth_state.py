from aiogram.dispatcher.filters.state import StatesGroup, State


class AuthState(StatesGroup):
    check_code = State()
