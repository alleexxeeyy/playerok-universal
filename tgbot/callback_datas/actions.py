from aiogram.filters.callback_data import CallbackData


class RememberUsername(CallbackData, prefix="rech"):
    name: str
    do: str

class RememberDealId(CallbackData, prefix="rede"):
    de_id: str
    do: str


class DeleteIncludedRestoreItem(CallbackData, prefix="delinre"):
    index: int

class DeleteExcludedRestoreItem(CallbackData, prefix="delexre"):
    index: int


class DeleteIncludedBumpItem(CallbackData, prefix="delinbu"):
    index: int

class DeleteExcludedBumpItem(CallbackData, prefix="delexbu"):
    index: int


class SelectBankCard(CallbackData, prefix="sebaca"):
    id: str

class SelectSbpBank(CallbackData, prefix="sesbp"):
    id: str


class SendLogsFile(CallbackData, prefix="selogs"):
    lines: int