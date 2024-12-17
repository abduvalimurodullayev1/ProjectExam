from aiogram.fsm.state import StatesGroup, State


class RegistrationStateGroup(StatesGroup):
    language = State()
    phone = State()
    name = State()



class MenuStateGroup(StatesGroup):
    menu = State()
    select_color = State()
    select_price = State()
    select_year = State()
    select_brand = State()
    select_model = State()
    add_filters = State()
    set_color = State()
    set_year = State()
    set_mileage = State()
    select_filters = State()





class FilterState(StatesGroup):
    select_color = State()
    select_price = State()
    select_year = State()
    mil = State


class DetectionState(StatesGroup):
    select_brand = State()
    select_model = State()
    add_filters = State()