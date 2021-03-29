import re
import phonenumbers
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from loguru import logger

from data.config import NUMBER_PATTERN


def parse_number(phone_number: str) -> str:
    # Парсим наш номер для добавление в бд
    parsed_number = phonenumbers.format_number(phonenumbers.parse(phone_number, 'RU'),
                                               phonenumbers.PhoneNumberFormat.NATIONAL).replace(" ", "")
    # Проверяем номер на возможные проблемы с форматированием и парсингом номеров
    if phone_number.find("+7", 0, 3) != -1 or phone_number.find("7", 0, 3) != -1:
        try:
            parsed_number = "+7" + parsed_number[1:].replace("+", "")
        except Exception as ex:
            logger.exception(repr(ex))
    return parsed_number


class IncorrectNumber(Exception):
    pass


async def check_correct_phone(msg: types.Message) -> str:
    default_number = msg.text
    if not re.match(NUMBER_PATTERN, default_number):
        logger.info("Invalid number at get_employee handler")
        await msg.answer('Вы ввели номер телефона в неверном формате.\n'
                         'Попробуйте ввести ещё раз!')
        raise IncorrectNumber()
    return default_number
