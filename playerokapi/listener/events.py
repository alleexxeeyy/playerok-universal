from ..enums import EventTypes
from .. import types
import time


class BaseEvent:
    """
    Базовый класс события.

    :param event_type: Тип события.
    :type event_type: `PlayerokAPI.enums.EventTypes`

    :param chat_obj: Объект чата, в котором произошло событие.
    :type chat_obj: `PlayerokAPI.types.Chat`
    """

    def __init__(self, event_type: EventTypes, chat_obj: types.Chat):
        self.type = event_type
        """ Тип события. """
        self.chat = chat_obj
        """ Объект чата, в котором произошло событие. """
        self.time = time.time()
        """ Время события. """


class ChatInitializedEvent(BaseEvent):
    """
    Класс события: обнаружен чат при первом запросе Runner'а.

    :param chat_obj: Объект обнаруженного чата.
    :type chat_obj: `PlayerokAPI.types.Chat`
    """

    def __init__(self, chat_obj: types.Chat):
        super(ChatInitializedEvent, self).__init__(
            EventTypes.CHAT_INITIALIZED, chat_obj
        )
        self.chat: types.Chat = chat_obj
        """ Объект обнаруженного чата. """


class NewMessageEvent(BaseEvent):
    """
    Класс события: новое сообщение в чате.

    :param message_obj: Объект полученного сообщения.
    :type message_obj: `PlayerokAPI.types.ChatMessage`

    :param chat_obj: Объект чата, в котором произошло событие.
    :type chat_obj: `PlayerokAPI.types.Chat`
    """

    def __init__(self, message_obj: types.ChatMessage, chat_obj: types.Chat):
        super(NewMessageEvent, self).__init__(EventTypes.NEW_MESSAGE, chat_obj)
        self.message: types.ChatMessage = message_obj
        """ Объект полученного сообщения. """


class NewDealEvent(BaseEvent):
    """
    Класс события: новая созданная сделка (когда покупатель оплатил предмет).

    :param deal_obj: Объект новой сделки.
    :type deal_obj: `PlayerokAPI.types.ItemDeal`

    :param chat_obj: Объект чата, в котором произошло событие.
    :type chat_obj: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal_obj: types.ItemDeal, chat_obj: types.Chat):
        super(NewDealEvent, self).__init__(EventTypes.NEW_DEAL, chat_obj)
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """


class NewReviewEvent(BaseEvent):
    """
    Класс события: новый отзыв от покупателя.

    :param deal_obj: Объект сделки с отзывом.
    :type deal_obj: `PlayerokAPI.types.ItemDeal`

    :param chat_obj: Объект чата, в котором произошло событие.
    :type chat_obj: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal_obj: types.ItemDeal, chat_obj: types.Chat):
        super(NewReviewEvent, self).__init__(EventTypes.NEW_REVIEW, chat_obj)
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """


class DealConfirmedEvent(BaseEvent):
    """
    Класс события: покупатель подтвердил сделку.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.ItemDeal`

    :param chat_obj: Объект чата, в котором произошло событие.
    :type chat_obj: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal_obj: types.ItemDeal, chat_obj: types.Chat):
        super(DealConfirmedEvent, self).__init__(EventTypes.DEAL_CONFIRMED, chat_obj)
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """


class DealRolledBackEvent(BaseEvent):
    """
    Класс события: продавец вернул средства за сделку.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.ItemDeal`

    :param chat_obj: Объект чата, в котором произошло событие.
    :type chat_obj: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal_obj: types.ItemDeal, chat_obj: types.Chat):
        super(DealRolledBackEvent, self).__init__(EventTypes.DEAL_ROLLED_BACK, chat_obj)
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """


class DealHasProblemEvent(BaseEvent):
    """
    Класс события: кто-то сообщил о проблеме в сделке.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.ItemDeal`

    :param chat_obj: Объект чата, в котором произошло событие.
    :type chat_obj: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal_obj: types.ItemDeal, chat_obj: types.Chat):
        super(DealHasProblemEvent, self).__init__(EventTypes.DEAL_HAS_PROBLEM, chat_obj)
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """


class DealProblemResolvedEvent(BaseEvent):
    """
    Класс события: проблема в сделке решена.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.ItemDeal`

    :param chat_obj: Объект чата, в котором произошло событие.
    :type chat_obj: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal_obj: types.ItemDeal, chat_obj: types.Chat):
        super(DealProblemResolvedEvent, self).__init__(
            EventTypes.DEAL_PROBLEM_RESOLVED, chat_obj
        )
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """


class DealStatusChangedEvent(BaseEvent):
    """
    Класс события: статус сделки изменён.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.ItemDeal`

    :param chat_obj: Объект чата, в котором произошло событие.
    :type chat_obj: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal_obj: types.ItemDeal, chat_obj: types.Chat):
        super(DealStatusChangedEvent, self).__init__(
            EventTypes.DEAL_STATUS_CHANGED, chat_obj
        )
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """


class ItemPaidEvent(BaseEvent):
    """
    Класс события: предмет оплачен.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.Item`

    :param chat_obj: Объект чата, в котором произошло событие.
    :type chat_obj: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal_obj: types.ItemDeal, chat_obj: types.Chat):
        super(ItemPaidEvent, self).__init__(EventTypes.ITEM_PAID, chat_obj)
        self.deal: types.ItemDeal = deal_obj
        """ Объект сделки. """


class ItemSentEvent(BaseEvent):
    """
    Класс события: предмет отправлен покупателю.

    :param deal_obj: Объект сделки.
    :type deal_obj: `PlayerokAPI.types.Item`

    :param chat_obj: Объект чата, в котором произошло событие.
    :type chat_obj: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal_obj: types.ItemDeal, chat_obj: types.Chat):
        super(ItemSentEvent, self).__init__(EventTypes.ITEM_SENT, chat_obj)
        self.deal: types.ItemDeal = deal_obj
        """ Объект Сделки. """