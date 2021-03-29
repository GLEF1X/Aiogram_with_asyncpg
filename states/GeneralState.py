from aiogram.dispatcher.filters.state import StatesGroup, State


class StartState(StatesGroup):
    in_general_menu = State()
    choosing_master_type = State()
    choosing_master_folder = State()
    choose_partner_type = State()
    choose_partner = State()


class SearchMaster(StatesGroup):
    enter_number = State()
    master_name = State()
    add_master = State()
    old_phone_number = State()
    new_phone_number = State()
    enter_comment = State()
    by_finish = State()
    last = State()


class AdminPanel(StatesGroup):
    in_admin = State()
    enter_master_id = State()
    choose_param_to_change = State()
    enter_param_value = State()
