from aiogram.filters.callback_data import CallbackData


class ModulesPagination(CallbackData, prefix="modpag"):
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


class BankCardsPagination(CallbackData, prefix="bacapag"):
    page: int

class SbpBanksPagination(CallbackData, prefix="sbppag"):
    page: int