from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from loader import manager

change_param = CallbackData('params', 'param', 'rus_param')

change_comment = CallbackData('comment_changer', 'employee_id', 'is_busy')


async def generate_markup_partner() -> ReplyKeyboardMarkup:
    services = await manager.partner.select_services()
    markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    for partner in services:
        markup.insert(
            KeyboardButton(text=partner.get('partner_service'))
        )
    markup.row(KeyboardButton(text='Вернуться назад'))
    return markup


def choose_type_master_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Плиточник', callback_data='Плиточник'),
                InlineKeyboardButton(text='Маляр', callback_data='Маляр')
            ],
        ]
    )


change_profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Комментарий',
                                 callback_data=change_param.new(param='comment', rus_param='комментарий')),
            InlineKeyboardButton(text='Имя', callback_data=change_param.new(param='name', rus_param='имя'))
        ],
        [
            InlineKeyboardButton(text='Номер телефона',
                                 callback_data=change_param.new(param='phone_number', rus_param='номер телефона'))
        ]
    ]
)


def change_comment_keyboard_generator(employee_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Занят',
                                     callback_data=change_comment.new(employee_id=employee_id, is_busy=True)),
                InlineKeyboardButton(text='Не занят',
                                     callback_data=change_comment.new(employee_id=employee_id, is_busy=False))
            ]
        ]
    )
    return markup


add_comment_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Занят',
                                 callback_data='Занят'),
            InlineKeyboardButton(text='Не занят',
                                 callback_data='Не занят')
        ]
    ]
)
