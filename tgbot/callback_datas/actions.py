from aiogram.filters.callback_data import CallbackData

class RememberUsername(CallbackData, prefix="rech"):
    name: str
    do: str

class RememberDealId(CallbackData, prefix="rede"):
    de_id: str
    do: str