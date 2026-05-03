from aiogram.filters.callback_data import CallbackData


class ModulesPagination(CallbackData, prefix="modpag"):
    page: int

class SignedUsersPagination(CallbackData, prefix="supag"):
    page: int


class IncludedRestoreItemsPagination(CallbackData, prefix="inrepag"):
    page: int

class ExcludedRestoreItemsPagination(CallbackData, prefix="exrepag"):
    page: int


class IncludedCompleteDealsPagination(CallbackData, prefix="incopag"):
    page: int

class ExcludedCompleteDealsPagination(CallbackData, prefix="excopag"):
    page: int


class IncludedBumpItemsPagination(CallbackData, prefix="inbupag"):
    page: int

class ExcludedBumpItemsPagination(CallbackData, prefix="exbupag"):
    page: int


class CustomCommandsPagination(CallbackData, prefix="cucopag"):
    page: int

class AutoDeliveriesPagination(CallbackData, prefix="audepag"):
    page: int

class DelivGoodsPagination(CallbackData, prefix="godspag"):
    page: int

class MessagesPagination(CallbackData, prefix="messpag"):
    page: int


class FastRepliesPagination(CallbackData, prefix="replpag"):
    page: int

class FastSelFastReplyPagination(CallbackData, prefix="fsrpag"):
    id: str
    page: int

class SelFastReplyPagination(CallbackData, prefix="srpag"):
    id: str
    page: int


class BankCardsPagination(CallbackData, prefix="bacapag"):
    page: int

class SbpBanksPagination(CallbackData, prefix="sbppag"):
    page: int


class ChatsPagination(CallbackData, prefix="chatpag"):
    page: int
    upd: bool = False

class DealsPagination(CallbackData, prefix="dealpag"):
    page: int
    upd: bool = False

class ItemsPagination(CallbackData, prefix="itpag"):
    page: int
    upd: bool = False

class TransactionsPagination(CallbackData, prefix="trpag"):
    page: int
    upd: bool = False

class ReviewsPagination(CallbackData, prefix="rvpag"):
    page: int
    upd: bool = False


class FastSelMessageTemplatePagination(CallbackData, prefix="fsmtpag"):
    id: str
    type: str
    page: int

class SelMessageTemplatePagination(CallbackData, prefix="smtpag"):
    id: str
    type: int
    page: int