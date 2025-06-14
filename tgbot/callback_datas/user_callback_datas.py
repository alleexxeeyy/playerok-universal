from aiogram.filters.callback_data import CallbackData
from uuid import UUID



class MenuNavigation(CallbackData, prefix="menpag"):
    """ Навигация в меню. """
    to: str


class SettingsNavigation(CallbackData, prefix="sepag"):
    """ Навигация в настройках. """
    to: str

class BotSettingsNavigation(CallbackData, prefix="bspag"):
    """ Навигация в настройках бота. """
    to: str

class ItemsSettingsNavigation(CallbackData, prefix="ispag"):
    """ Навигация в настройках лотов. """
    to: str

class InstructionNavigation(CallbackData, prefix="inspag"):
    """ Навигация в инструкции. """
    to: str


class ModulesPagination(CallbackData, prefix="modpag"):
    """ Пагинация в модулях. """
    page: int

class ModulePage(CallbackData, prefix="modpage"):
    """ Страница модуля. """
    uuid: UUID


class ActiveOrdersPagination(CallbackData, prefix="aopag"):
    """ Пагинация в активных заказах. """
    page: int

class ActiveOrderPage(CallbackData, prefix="aopag"):
    """ Пагинация в активных заказах. """
    order_id: str


class CustomCommandsPagination(CallbackData, prefix="cucopag"):
    """ Пагинация в пользовательских командах. """
    page: int

class CustomCommandPage(CallbackData, prefix="cucopage"):
    """ Страница пользовательской команды. """
    command: str


class AutoDeliveriesPagination(CallbackData, prefix="audepag"):
    """ Пагинация в авто-доставках. """
    page: int

class AutoDeliveryPage(CallbackData, prefix="audepage"):
    """ Страница авто-выдачи. """
    item_id: str


class MessagesPagination(CallbackData, prefix="messpag"):
    """ Пагинация в сообщениях. """
    page: int

class MessagePage(CallbackData, prefix="messpage"):
    """ Страница сообщения. """
    message_id: str