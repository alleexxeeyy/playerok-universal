from aiogram.filters.callback_data import CallbackData


class SendFastReply(CallbackData, prefix="sere"):
    id: str
    index: int

class FastSendFastReply(CallbackData, prefix="fsere"):
    id: str
    index: int


class FastChangeDealStatus(CallbackData, prefix="fchds"):
    id: str
    st: str

class ChangeDealStatus(CallbackData, prefix="chds"):
    id: str
    st: str


class FastSelMessageTemplate(CallbackData, prefix="fsmt"):
    id: str

class SelMessageTemplate(CallbackData, prefix="smt"):
    id: str

class FastReportDealProblem(CallbackData, prefix="frdp"):
    id: str

class ReportDealProblem(CallbackData, prefix="rdp"):
    id: str


class PublishItem(CallbackData, prefix="pit"):
    id: str

class IncreaseItemPriority(CallbackData, prefix="iipr"):
    id: str

class DeleteItem(CallbackData, prefix="dit"):
    id: str
