from aiogram import types
from loguru import logger

from filters.StartFilters import IsRegistered
from keyboards.default.start_keyboards import generate_keyboard_by_partners
from keyboards.inline.inline_keyboards import generate_markup_partner
from loader import dp, manager
from states.GeneralState import StartState


@dp.message_handler(text='Вернуться назад', state=StartState.choose_partner)
@dp.message_handler(IsRegistered(), text='Партнеры', state='*')
async def get_partners(message: types.Message):
    markup = await generate_markup_partner()
    await message.answer(
        text='Выбери партнера',
        reply_markup=markup
    )
    await StartState.choose_partner_type.set()


@dp.message_handler(state=StartState.choose_partner_type)
async def partners_by_name(message: types.Message):
    keyboard = await generate_keyboard_by_partners(message)
    await message.answer(
        text='Выберите партнера',
        reply_markup=keyboard
    )
    await StartState.choose_partner.set()


@dp.message_handler(state=StartState.choose_partner)
async def choose_partner(message: types.Message) -> None:
    company_name = message.text
    partner = await manager.partner.select_entry(
        company_name=company_name
    )
    if not partner:
        logger.error('Нет информации о партнере')
        await message.answer('Нет информации по этому партнеру.')
        return
    text = f"""{partner.get('company_name')}
Контактное имя: {partner.get('contact_name')}
Номер телефона: {partner.get('contact_number')}
"""
    if i_link := partner.get('instagram_link'):
        text += f'\n<a href="{i_link}">instagram</a>'
    elif w_link := partner.get('whatsapp_link'):
        text += f'\n<a href="{w_link}">Whatsapp</a>'
    text += f"\nОписание: {partner.get('comment') if isinstance(partner.get('comment'), str) else '-'}"
    text += """

"""
    await message.answer(
        text=text, disable_web_page_preview=True
    )
