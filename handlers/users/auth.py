from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.handler import CancelHandler

from filters.StartFilters import IsNotRegistered
from keyboards.default.start_keyboards import generate_start_keyboard
from loader import dp
from states.GeneralState import StartState
from states.auth_state import AuthState
from utils.db_api.fast_commands import check_promo


@dp.message_handler(IsNotRegistered(), CommandStart(), state=AuthState.check_code)
@dp.message_handler(IsNotRegistered(), CommandStart())
async def check_auth(message: types.Message):
    await message.answer(
        text='Пожалуйста, введите специальный код доступа, чтобы пользоваться функциями бота.'
    )
    await AuthState.check_code.set()


@dp.message_handler(state=AuthState.check_code)
async def handle_code(message: types.Message):
    answer = await check_promo(message)
    if not answer:
        raise CancelHandler()
    await message.answer('Вы успешно зарегистрировались в боте используя код доступа',
                         reply_markup=generate_start_keyboard(message))
    await StartState.in_general_menu.set()
