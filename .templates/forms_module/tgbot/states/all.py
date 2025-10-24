from aiogram.fsm.state import State, StatesGroup
    

class FORMS_MessagesStates(StatesGroup):
    entering_page = State()

class FORMS_MessagePageStates(StatesGroup):
    entering_message_text = State()