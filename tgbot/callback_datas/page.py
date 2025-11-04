from aiogram.filters.callback_data import CallbackData
from uuid import UUID


class ModulePage(CallbackData, prefix="modpage"):
    uuid: UUID


class MessagePage(CallbackData, prefix="messpage"):
    message_id: str


class CustomCommandPage(CallbackData, prefix="cucopage"):
    command: str


class AutoDeliveryPage(CallbackData, prefix="audepage"):
    index: int