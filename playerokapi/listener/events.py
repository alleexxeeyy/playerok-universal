from ..enums import EventTypes
from .. import types
import time

class BaseEvent:
    """
    Базовый класс события.

    :param event_type: Тип события.
    :type event_type: `PlayerokAPI.enums.EventTypes`
    """
    def __init__(self, event_type: EventTypes):
        self.type = event_type
        """ Тип события. """
        self.time = time.time()
        """ Время события. """

class ChatInitializedEvent(BaseEvent):
    """
    Класс события: обнаружен чат при первом запросе Runner'а.

    :param chat_obj: Объект обнаруженного чата.
    :type chat_obj: `PlayerokAPI.types.Chat`
    """
    def __init__(self, chat_obj: types.Chat):
        super(ChatInitializedEvent, self).__init__(EventTypes.CHAT_INITIALIZED)
        self.chat: types.Chat = chat_obj
        """ Объект обнаруженного чата. """

class NewMessageEvent(BaseEvent):
    """
    Класс события: новое сообщение в чате.

    :param message_obj: Объект полученного сообщения.
    :type message_obj: `PlayerokAPI.types.ChatMessage`
    """
    def __init__(self, message_obj: types.ChatMessage):
        super(NewMessageEvent, self).__init__(EventTypes.NEW_MESSAGE)
        self.message: types.ChatMessage = message_obj
        """ Объект полученного сообщения. """

class NewDealEvent(BaseEvent):
    """
    Класс события: новая созданная сделка (когда покупатель оплатил предмет).

    :param deal_obj: Объект новой сделки.
    :type deal_obj: `PlayerokAPI.types.ItemDeal`
    """
    def __init__(self, deal_obj: types.ItemDeal):
        super(NewDealEvent, self).__init__(EventTypes.NEW_DEAL)
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """

class DealConfirmedEvent(BaseEvent):
    """
    Класс события: покупатель подтвердил сделку.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.ItemDeal`
    """
    def __init__(self, deal_obj: types.ItemDeal):
        super(DealConfirmedEvent, self).__init__(EventTypes.DEAL_CONFIRMED)
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """

class DealRolledBackEvent(BaseEvent):
    """
    Класс события: продавец вернул средства за сделку.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.ItemDeal`
    """
    def __init__(self, deal_obj: types.ItemDeal):
        super(DealRolledBackEvent, self).__init__(EventTypes.DEAL_ROLLED_BACK)
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """

class DealHasProblemEvent(BaseEvent):
    """
    Класс события: кто-то сообщил о проблеме в сделке.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.ItemDeal`
    """
    def __init__(self, deal_obj: types.ItemDeal):
        super(DealHasProblemEvent, self).__init__(EventTypes.DEAL_HAS_PROBLEM)
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """

class DealProblemResolvedEvent(BaseEvent):
    """
    Класс события: проблема в сделке решена.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.ItemDeal`
    """
    def __init__(self, deal_obj: types.ItemDeal):
        super(DealProblemResolvedEvent, self).__init__(EventTypes.DEAL_PROBLEM_RESOLVED)
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """

class DealStatusChangedEvent(BaseEvent):
    """
    Класс события: статус сделки изменён.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.ItemDeal`
    """
    def __init__(self, deal_obj: types.ItemDeal):
        super(DealStatusChangedEvent, self).__init__(EventTypes.DEAL_STATUS_CHANGED)
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """

class ItemPaidEvent(BaseEvent):
    """
    Класс события: предмет оплачен.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.Item`
    """
    def __init__(self, deal_obj: types.ItemDeal):
        super(ItemPaidEvent, self).__init__(EventTypes.ITEM_PAID)
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """

class ItemSentEvent(BaseEvent):
    """
    Класс события: предмет отправлен покупателю.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.Item`
    """
    def __init__(self, deal_obj: types.ItemDeal):
        super(ItemSentEvent, self).__init__(EventTypes.ITEM_SENT)
        self.deal: types.ItemDeal = deal_obj
        """ Объект Сделки. """