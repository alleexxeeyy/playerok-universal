from aiogram.filters.callback_data import CallbackData
from uuid import UUID



class MenuNavigation(CallbackData, prefix="menpag"):
    to: str


class SettingsNavigation(CallbackData, prefix="sepag"):
    to: str

class BotSettingsNavigation(CallbackData, prefix="bspag"):
    to: str

class ItemsSettingsNavigation(CallbackData, prefix="ispag"):
    to: str

class InstructionNavigation(CallbackData, prefix="inspag"):
    to: str


class ModulesPagination(CallbackData, prefix="modpag"):
    page: int

class ModulePage(CallbackData, prefix="modpage"):
    uuid: UUID


class CustomCommandsPagination(CallbackData, prefix="cucopag"):
    page: int

class CustomCommandPage(CallbackData, prefix="cucopage"):
    command: str


class AutoDeliveriesPagination(CallbackData, prefix="audepag"):
    page: int

class AutoDeliveryPage(CallbackData, prefix="audepage"):
    index: int


class MessagesPagination(CallbackData, prefix="messpag"):
    page: int

class MessagePage(CallbackData, prefix="messpage"):
    message_id: str