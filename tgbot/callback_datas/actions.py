from aiogram.filters.callback_data import CallbackData


class DeleteSignedUser(CallbackData, prefix="desu"):
    id: int

class RememberChatId(CallbackData, prefix="rech"):
    id: str
    do: str

class RememberDealId(CallbackData, prefix="rede"):
    de_id: str
    do: str


class DeleteIncludedRestoreItem(CallbackData, prefix="delinre"):
    index: int

class DeleteExcludedRestoreItem(CallbackData, prefix="delexre"):
    index: int


class DeleteIncludedCompleteDeal(CallbackData, prefix="delinco"):
    index: int

class DeleteExcludedCompleteDeal(CallbackData, prefix="delexco"):
    index: int


class DeleteIncludedBumpItem(CallbackData, prefix="delinbu"):
    index: int

class DeleteExcludedBumpItem(CallbackData, prefix="delexbu"):
    index: int


class EnterFastReplyText(CallbackData, prefix="enrepl"):
    index: int

class DeleteFastReply(CallbackData, prefix="delrepl"):
    index: int


class SelectBankCard(CallbackData, prefix="sebaca"):
    id: str

class SelectSbpBank(CallbackData, prefix="sesbp"):
    id: str


class SendLogsFile(CallbackData, prefix="selogs"):
    lines: int


class SetNewDelivPiece(CallbackData, prefix="sepiece"):
    val: bool

class DeleteDelivGood(CallbackData, prefix="delgod"):
    index: int


class ChangeDealsFilter(CallbackData, prefix="chdf"):
    di: int = -1
    st: int = -1

class ChangeItemsFilter(CallbackData, prefix="chif"):
    st: int = -1
    ga_id: str = ""
    ca_id: str = ""

class ChangeTransactionsFilter(CallbackData, prefix="chtf"):
    st: int = -1
    op: int = -1
    pr: int = -1
    min_val: int = -1
    max_val: int = -1
    from_dt: str = ""
    to_dt: str = ""

class ChangeReviewsFilter(CallbackData, prefix="chrf"):
    st: int = -1
    cr: int = -1
    rt: int = -1
    ga_id: str = ""
    ca_id: str = ""
    min_pr: int = -1
    max_pr: int = -1


class ConfirmPublishItem(CallbackData, prefix="cpit"):
    st_id: str