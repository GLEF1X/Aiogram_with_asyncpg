from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher.handler import CancelHandler

from filters.StartFilters import IsRegistered
from keyboards.default.start_keyboards import master_types_keyboard, generate_markup_folders, \
    generate_start_keyboard
from keyboards.inline.inline_keyboards import change_comment, change_comment_keyboard_generator
from loader import dp, bot, manager
from states.GeneralState import StartState, SearchMaster, AdminPanel


@dp.message_handler(text='Вернуться назад', state=AdminPanel.all_states)
@dp.message_handler(text='Вернуться назад', state=SearchMaster.all_states)
@dp.message_handler(text='Вернуться назад', state=StartState.choose_partner_type)
@dp.message_handler(text='Вернуться назад', state=StartState.choosing_master_type)
@dp.message_handler(IsRegistered(), CommandStart(), state='*')
async def start(message: types.Message):
    await message.answer(
        text='Вы в главном меню!',
        reply_markup=generate_start_keyboard(message)
    )
    await StartState.in_general_menu.set()


@dp.message_handler(text='Назад', state=StartState.choosing_master_folder)
@dp.message_handler(text='Мастера', state=StartState.in_general_menu)
async def get_masters(message: types.Message):
    markup = await master_types_keyboard()
    await message.answer(
        text='Выберите категорию',
        reply_markup=markup
    )
    await StartState.choosing_master_type.set()


@dp.message_handler(state=StartState.choosing_master_type)
async def get_master_folders(message: types.Message, state: FSMContext):
    if message.text not in ['Плиточники', 'Маляры']:
        raise CancelHandler()
    markup, masters = await generate_markup_folders(message.text)
    await bot.send_message(
        text='В каждой папке по 10 мастеров',
        chat_id=message.from_user.id,
        reply_markup=markup
    )
    await StartState.choosing_master_folder.set()
    await state.update_data(
        master_type=message.text
    )


@dp.message_handler(state=StartState.choosing_master_folder)
async def get_masters_by_folder(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        master_type = data.get('master_type')
    if not message.text.replace('Папка', '').isdigit():
        raise CancelHandler()
    masters = await manager.employee.get_by_type(master_type)
    start_index = (int(message.text.replace("Папка", "")) - 1) * 10
    end_index = start_index + 10
    for i in range(start_index, end_index):
        try:
            text = f"""{masters[i].get('employee_id')}.
Имя: {masters[i].get('name')}
Номер: {masters[i].get('phone_number')}
Тип занятости: {masters[i].get('type_of_employment') if masters[i].get('type_of_employment') is not None else '-'}\n
Комментарий: {masters[i].get('comment') if masters[i].get('comment') is not None else '-'}"""
        except IndexError:
            break
        await bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=change_comment_keyboard_generator(masters[i].get('employee_id'))
        )


@dp.callback_query_handler(change_comment.filter(), state=StartState.choosing_master_folder)
async def change_comment(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    employee_id = callback_data.get('employee_id')
    is_busy = callback_data.get('is_busy')
    comment = 'Занят'
    if is_busy == 'False':
        comment = 'Не занят'
    employee = await manager.employee.update_entry(
        update_values={
            'type_of_employment': comment
        },
        employee_id=int(employee_id)
    )
    await call.answer(text='Комментарий успешно изменен', show_alert=True, cache_time=20)
    await call.message.edit_text(
        text=f"""{employee.get('employee_id')}.
Имя: {employee.get('name')}
Номер: {employee.get('phone_number')}
Тип занятости: {comment}

Комментарий: {employee.get('comment') if isinstance(employee.get('comment'), str) else '-'}""",
        reply_markup=change_comment_keyboard_generator(employee.get('employee_id'))
    )
