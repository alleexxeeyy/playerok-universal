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


class ChatPage(CallbackData, prefix="chtpage"):
    id: str

class DealPage(CallbackData, prefix="deapage"):
    id: str

class ItemPage(CallbackData, prefix="itpage"):
    id: str

class TransactionPage(CallbackData, prefix="trpage"):
    id: str

class ReviewPage(CallbackData, prefix="rvpage"):
    id: str
