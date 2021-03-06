from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Редактировать профиль мастера'),
            KeyboardButton(text='Получить промокоды')
        ],
        [
            KeyboardButton(text='Добавить партнера')
        ],
        [
            KeyboardButton(text='Вернуться назад')
        ]
    ], resize_keyboard=True
)
