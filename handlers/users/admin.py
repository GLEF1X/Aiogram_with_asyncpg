import re
from typing import Dict

import asyncpg
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import CancelHandler
from loguru import logger

from data.config import NUMBER_PATTERN
from filters.StartFilters import IsAdmin
from keyboards.default.admin_keyboards import admin_start_keyboard
from keyboards.default.start_keyboards import cancel_keyboard, generate_start_keyboard
from keyboards.inline.inline_keyboards import change_profile_keyboard, change_param
from loader import dp, manager
from states.GeneralState import AdminPanel, StartState
from utils.misc.help_functions import parse_number


@dp.message_handler(IsAdmin(), text='Админка', state=StartState.in_general_menu)
async def admin_panel(message: types.Message):
    await AdminPanel.in_admin.set()
    await message.answer(
        text='Вы в админ-панели',
        reply_markup=admin_start_keyboard
    )


@dp.message_handler(text='Редактировать профиль мастера', state=AdminPanel.in_admin)
async def edit_master_profile(message: types.Message):
    await message.answer(
        'Введите номер мастера, которого вы хотите отредактировать',
        reply_markup=cancel_keyboard
    )
    await AdminPanel.enter_master_id.set()


@dp.message_handler(state=AdminPanel.enter_master_id)
async def change_profile(msg: types.Message, state: FSMContext):
    try:
        master = await manager.employee.select_entry(
            employee_id=int(msg.text)
        )
        if not isinstance(master, asyncpg.Record):
            raise TypeError()
    except TypeError:
        await msg.answer('Вы неправильно ввели номер работника или мастера с таким номером нет в базе данных')
        return
    await msg.answer('Выберите, что вы хотите поменять', reply_markup=change_profile_keyboard)
    await state.update_data(
        employee_id=master.get('employee_id'),
        contact_name=master.get('name')
    )
    await AdminPanel.choose_param_to_change.set()


@dp.callback_query_handler(change_param.filter(), state=AdminPanel.choose_param_to_change)
async def change_something(call: types.CallbackQuery, state: FSMContext, callback_data: Dict[str, str]):
    async with state.proxy() as data:
        contact_name = data.get('contact_name')
    await call.message.answer(f'Введите новый {callback_data.get("rus_param")} для работника {contact_name}')
    await state.update_data(
        update_param=callback_data.get("param")
    )
    await AdminPanel.enter_param_value.set()


@dp.message_handler(state=AdminPanel.enter_param_value)
async def check_and_change_master_param(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        contact_name = data.get('contact_name')
        employee_id = data.get('employee_id')
        update_param = data.get('update_param')
    value = message.text
    if update_param == 'phone_number':
        default_number = message.text
        if not re.match(NUMBER_PATTERN, default_number):
            logger.info("Invalid number at get_employee handler")
            await message.answer('Вы ввели номер телефона в неверном формате.\n'
                                 'Попробуйте ввести ещё раз!')
            raise CancelHandler()
        value = parse_number(default_number)
        if value.find("+") == -1:
            value = "+" + value
        await message.answer(f'Вы успешно изменили номер телефона {contact_name}',
                             reply_markup=generate_start_keyboard(message))
    elif update_param == 'name':
        await message.answer(f'Вы успешно изменили имя мастера на {message.text}',
                             reply_markup=generate_start_keyboard(message))
    else:
        await message.answer(f'Вы успешно изменили комментарий мастера на "{message.text}"',
                             reply_markup=generate_start_keyboard(message))
    await manager.employee.update_entry(
        update_values={
            update_param: value
        },
        employee_id=employee_id
    )
    await StartState.in_general_menu.set()
