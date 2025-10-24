from aiogram.filters.callback_data import CallbackData


class FORMS_MenuNavigation(CallbackData, prefix="forms_mennav"):
    to: str
    
class FORMS_InstructionNavigation(CallbackData, prefix="forms_inspag"):
    to: str

class FORMS_MessagesPagination(CallbackData, prefix="forms_mespag"):
    page: int

class FORMS_MessagePage(CallbackData, prefix="forms_mespage"):
    message_id: str