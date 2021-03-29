import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asyncpg import Record
from loguru import logger

from data.config import NUMBER_PATTERN
from keyboards.default.start_keyboards import cancel_keyboard, add_master_keyboard, \
    generate_start_keyboard
from keyboards.inline.inline_keyboards import choose_type_master_keyboard
from loader import dp, manager
from states.GeneralState import StartState, SearchMaster
from utils.misc.help_functions import parse_number


@dp.message_handler(text='Поиск мастера', state=StartState.in_general_menu)
async def search_master(msg: types.Message):
    await msg.answer("""Пришли номер телефона в формате 89990009900""", reply_markup=cancel_keyboard)
    await SearchMaster.enter_number.set()


@dp.message_handler(state=SearchMaster.enter_number)
async def get_employee(msg: types.Message, state: FSMContext):
    default_number = msg.text
    if not re.match(NUMBER_PATTERN, default_number):
        logger.info("Invalid number at get_employee handler")
        await msg.answer('Вы ввели номер телефона в неверном формате.\n'
                         'Попробуйте ввести ещё раз!')
        raise CancelHandler()
    number = parse_number(default_number)
    master = await manager.employee.select_master_by_phone(
        phone_number=number,
        default_number=default_number
    )
    if not isinstance(master, Record):
        await msg.answer('Такого мастера не найдено.\n'
                         'Можешь добавить его в базу, нажав на кнопку ниже', reply_markup=add_master_keyboard)
        await state.update_data(
            phone_number=default_number
        )
        await SearchMaster.add_master.set()
        raise CancelHandler()
    text = f"""Номер в базе данных: {master.get('employee_id')}
Имя: {master.get('name')}
Номер: {master.get('phone_number')}
Комментарий: {master.get('comment') if master.get('comment') is not None else '-'}\n"""
    await msg.answer(
        text=text,
        reply_markup=generate_start_keyboard(msg)
    )
    await StartState.in_general_menu.set()


@dp.message_handler(text='Добавить мастера', state=SearchMaster.add_master)
async def add_master(msg: types.Message):
    await msg.answer(
        'Введите имя мастера',
        reply_markup=cancel_keyboard
    )
    await SearchMaster.master_name.set()


@dp.message_handler(state=SearchMaster.master_name)
async def enter_master_number(msg: types.Message, state: FSMContext):
    await state.update_data(
        name=msg.text
    )
    await msg.answer(
        'Хотите ли вы использовать номер телефона, который вы использовали при поиске',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Да, использовать старый', callback_data='use_old_number')
                ],
                [
                    InlineKeyboardButton(text='Нет, ввести другой', callback_data='enter_new_number')
                ]
            ]
        )
    )
    await SearchMaster.old_phone_number.set()


@dp.callback_query_handler(state=SearchMaster.old_phone_number, text='use_old_number')
async def enter_comment(call: types.CallbackQuery):
    await call.message.answer(
        text='Отлично, введите комментарий к работнику'
    )
    await SearchMaster.enter_comment.set()


@dp.callback_query_handler(state=SearchMaster.old_phone_number, text='enter_new_number')
async def enter_phone_number(call: types.CallbackQuery):
    await call.message.answer('Пришли номер телефона в формате 89990009900')
    await SearchMaster.new_phone_number.set()


@dp.message_handler(state=SearchMaster.new_phone_number)
async def enter_comment_2(msg: types.Message, state: FSMContext):
    if not re.match(NUMBER_PATTERN, msg.text):
        logger.info("Invalid number at get_employee handler")
        await msg.answer('Вы ввели номер телефона в неверном формате.\n'
                         'Попробуйте ввести ещё раз!')
        raise CancelHandler()
    await state.update_data(phone_number=msg.text)
    await msg.answer(
        text='Отлично, введите комментарий к работнику'
    )
    await SearchMaster.enter_comment.set()


@dp.message_handler(state=SearchMaster.enter_comment)
async def choose_employee_type(msg: types.Message, state: FSMContext):
    await state.update_data(
        comment=msg.text
    )
    await msg.answer('Выберите тип работника', reply_markup=choose_type_master_keyboard())
    await SearchMaster.by_finish.set()


@dp.callback_query_handler(state=SearchMaster.by_finish)
async def add_master(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        phone_number: str = data.get('phone_number')
        name: str = data.get('name')
        comment: str = data.get('comment')
        master_type: str = call.data
    parsed_number = parse_number(phone_number)
    if parsed_number.find("+") == -1:
        parsed_number = "+" + parsed_number
    text = f"""Имя: {name}
Номер: {parsed_number}
Комментарий: {comment}
Специализация работника: {master_type}"""
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Да, добавить', callback_data='add_new')
            ],
            [
                InlineKeyboardButton(text='Нет, не добавлять', callback_data='finish')
            ]
        ]
    )
    await call.message.edit_text('Вы действительно хотите добавить работника?\n'
                                 f'{text}', reply_markup=markup)
    await SearchMaster.last.set()
    await state.update_data(
        master_type=master_type,
        phone_number=parsed_number
    )


@dp.callback_query_handler(state=SearchMaster.last, text='add_new')
async def add_new_master(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        phone_number = data.get('phone_number')
        name = data.get('name')
        comment = data.get('comment')
        master_type = data.get('master_type')
    await manager.employee.add_entry(
        employee_type=master_type,
        comment=comment,
        name=name,
        phone_number=phone_number
    )
    await call.message.answer('Успешно добавил нового сотрудника',
                              reply_markup=generate_start_keyboard(call))
    await state.reset_data()
    await StartState.in_general_menu.set()


@dp.callback_query_handler(state=SearchMaster.last, text='finish')
async def not_add_master(call: types.CallbackQuery, state: FSMContext):
    await state.reset_data()
    await StartState.in_general_menu.set()
    await call.message.answer('Вы успешно отменили добавление работника',
                              reply_markup=generate_start_keyboard(call))