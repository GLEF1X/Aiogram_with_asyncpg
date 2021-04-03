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
from keyboards.inline.inline_keyboards import change_profile_keyboard, change_param, add_partner_keyboard
from loader import dp, manager
from states.GeneralState import AdminPanel, StartState, AddPartner
from utils.misc.help_functions import parse_number


@dp.message_handler(IsAdmin(), text='Админка', state=StartState.in_general_menu)
async def admin_panel(message: types.Message):
    await AdminPanel.in_admin.set()
    await message.answer(
        text='Вы в админ-панели',
        reply_markup=admin_start_keyboard
    )


@dp.message_handler(text='Получить промокоды', state=AdminPanel.in_admin)
async def get_promo(message: types.Message):
    promo_codes = await manager.promo_code.select_all()
    text = ""
    for index, promo in enumerate(promo_codes, start=1):
        text += f"{index}. {promo.get('promo_value')}\n"
    await message.answer(text)


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


@dp.message_handler(text='Добавить партнера', state=AdminPanel.in_admin)
async def add_sponsor(message: types.Message):
    await message.answer(text='Введите название сервиса спонсора', reply_markup=cancel_keyboard)
    await AddPartner.enter_partner_service.set()


@dp.message_handler(state=AddPartner.enter_partner_service)
async def add_partner(message: types.Message, state: FSMContext):
    await state.update_data(partner_service=message.text)
    await message.answer('Введите имя комании', reply_markup=cancel_keyboard)
    await AddPartner.enter_company_name.set()


@dp.message_handler(state=AddPartner.enter_company_name)
async def enter_company_name(message: types.Message, state: FSMContext):
    await state.update_data(company_name=message.text)
    await message.answer('Введите контактное имя партнера', reply_markup=cancel_keyboard)
    await AddPartner.enter_contact_name.set()


@dp.message_handler(state=AddPartner.enter_contact_name)
async def enter_insta_link(message: types.Message, state: FSMContext):
    await state.update_data(contact_name=message.text)
    await message.answer('Введите ссылку на инстаграм или "-", если не хотите её добавлять',
                         reply_markup=cancel_keyboard)
    await AddPartner.enter_insta_link.set()


@dp.message_handler(state=AddPartner.enter_insta_link)
async def enter_whatsapp_link(message: types.Message, state: FSMContext):
    await state.update_data(instagram_link=message.text)
    await message.answer('Введите ссылку на whatsapp партнера или "-", если не хотите её добавлять')
    await AddPartner.enter_whatsapp_link.set()


@dp.message_handler(state=AddPartner.enter_whatsapp_link)
async def enter_contact_name(message: types.Message, state: FSMContext):
    await state.update_data(whatsapp_link=message.text)
    await message.answer('Введите контактный номер партнера', reply_markup=cancel_keyboard)
    await AddPartner.enter_contact_number.set()


@dp.message_handler(state=AddPartner.enter_contact_number)
async def enter_contact_number(message: types.Message, state: FSMContext):
    default_number = message.text
    if not re.match(NUMBER_PATTERN, default_number) or len(message.text) > 12 or len(message.text) < 10:
        logger.info("Invalid number at get_employee handler")
        await message.answer('Вы ввели номер телефона в неверном формате.\n'
                             'Попробуйте ввести ещё раз!')
        raise CancelHandler()
    value = parse_number(default_number)
    if value.find("+") == -1:
        value = "+" + value
    await state.update_data(contact_number=value)
    await message.answer('Введите комментарий к партнеру')
    await AddPartner.enter_comment.set()


@dp.message_handler(state=AddPartner.enter_comment)
async def enter_comment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        partner_service = data.get('partner_service')
        company_name = data.get('company_name')
        instagram_link = data.get('instagram_link')
        whatsapp_link = data.get('whatsapp_link')
        contact_number = data.get('contact_number')
        contact_name = data.get('contact_name')
        comment = message.text
    kwargs = {}
    kwargs.update(
        {'partner_service': partner_service,
         'company_name': company_name,
         'instagram_link': instagram_link,
         'whatsapp_link': whatsapp_link,
         'contact_number': contact_number,
         'contact_name': contact_name,
         'comment': comment}
    )
    await state.update_data(
        kwargs=kwargs
    )
    partner_info = text = f"""{company_name}
Контактное имя: {contact_name}
Номер телефона: {contact_number}
"""
    if i_link := instagram_link:
        text += f'\n<a href="{i_link}">instagram</a>'
    elif w_link := whatsapp_link:
        text += f'\n<a href="{w_link}">Whatsapp</a>'
    text += f"\nОписание: {comment if isinstance(comment, str) else '-'}"
    text += """

"""
    await message.answer(f'Вы действительно хотите добавить партнера: \n{partner_info}',
                         reply_markup=add_partner_keyboard)
    await AddPartner.final.set()


@dp.callback_query_handler(state=AddPartner.final, text='add_partner')
async def add_partner(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        kwargs = data.get('kwargs')
    await manager.partner.add_entry(**kwargs)
    await call.message.answer('Вы успешно добавили нового партнера')
    await state.reset_data()
    await StartState.in_general_menu.set()


@dp.callback_query_handler(text='reset', state=AddPartner.final)
async def reset_adding(call: types.CallbackQuery, state: FSMContext):
    await state.reset_data()
    await call.message.answer('Вы успешно отменили добавление партнера', reply_markup=admin_start_keyboard)
    await StartState.in_general_menu.set()
