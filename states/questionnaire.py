from aiogram.fsm.state import State, StatesGroup


class QuestionnaireStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_gender = State()
    waiting_for_genres = State()
    waiting_for_scenario = State()
    waiting_for_birthday = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_email_confirm = State()

