from typing import Tuple, Optional, List, Union

from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from asyncpg import Record

from data.config import ADMINS
from loader import manager
from utils.db_api.fast_commands import get_master_types


def generate_start_keyboard(query: Union[types.Message, types.CallbackQuery]) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Мастера'),
                KeyboardButton(text='Партнеры')
            ],
            [
                KeyboardButton(text='Поиск мастера')
            ]
        ], resize_keyboard=True
    )
    if query.from_user.id in ADMINS:
        markup.insert(
            KeyboardButton(text='Админка')
        )
    return markup


cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Вернуться назад')
        ]
    ], resize_keyboard=True
)


async def master_types_keyboard() -> ReplyKeyboardMarkup:
    master_types = await get_master_types()
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    [markup.insert(t.get('type') + "ы" if t.get('type') == 'Маляр' else t.get('type') + "и") for t in master_types]
    markup.row(
        KeyboardButton(text='Вернуться назад')
    )
    return markup


async def generate_markup_folders(master_type: str) -> Tuple[ReplyKeyboardMarkup, Optional[List[Record]]]:
    masters = await manager.employee.get_by_type(master_type)
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    folders = (len(masters) // 10) + 1
    for f_number in range(folders):
        markup.insert(KeyboardButton(text=f'Папка{f_number + 1}'))
    markup.row(
        KeyboardButton(text='Назад')
    )
    return markup, masters
    # for i, m in enumerate(masters, start=1):
    #     text = f"""{i}.
    # Имя: {m.get('name')}
    # Номер: {m.get('phone_number')}
    # Комментарий: {m.get('comment') if m.get('comment') is not None else '-'}\n"""


async def generate_keyboard_by_partners(message: types.Message) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    partner_service = message.text
    partners = await manager.partner.select_entry(
        partner_service=partner_service,
        fetch_all=True
    )
    for partner in partners:
        markup.insert(
            KeyboardButton(text=partner.get('company_name'))
        )
    markup.insert(
        KeyboardButton(text='Вернуться назад')
    )
    return markup


add_master_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Добавить мастера')
        ],
        [
            KeyboardButton(text='Вернуться назад')
        ]
    ], resize_keyboard=True
)
