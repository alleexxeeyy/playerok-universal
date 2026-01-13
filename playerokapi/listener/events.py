from ..enums import EventTypes
from .. import types
import time


class BaseEvent:
    """
    Базовый класс события.

    :param event_type: Тип события.
    :type event_type: `PlayerokAPI.enums.EventTypes`

    :param chat: Объект чата, в котором произошло событие.
    :type chat: `PlayerokAPI.types.Chat`
    """

    def __init__(self, event_type: EventTypes, chat: types.Chat):
        self.type = event_type
        """ Тип события. """
        self.chat = chat
        """ Объект чата, в котором произошло событие. """
        self.time = time.time()
        """ Время события. """


class ChatInitializedEvent(BaseEvent):
    """
    Класс события: обнаружен чат при первом запросе Runner'а.

    :param chat: Объект обнаруженного чата.
    :type chat: `PlayerokAPI.types.Chat`
    """

    def __init__(self, chat: types.Chat):
        super(ChatInitializedEvent, self).__init__(
            EventTypes.CHAT_INITIALIZED, chat
        )
        self.chat: types.Chat = chat
        """ Объект обнаруженного чата. """


class NewMessageEvent(BaseEvent):
    """
    Класс события: новое сообщение в чате.

    :param message: Объект полученного сообщения.
    :type message: `PlayerokAPI.types.ChatMessage`

    :param chat: Объект чата, в котором произошло событие.
    :type chat: `PlayerokAPI.types.Chat`
    """

    def __init__(self, message: types.ChatMessage, chat: types.Chat):
        super(NewMessageEvent, self).__init__(EventTypes.NEW_MESSAGE, chat)
        self.message: types.ChatMessage = message
        """ Объект полученного сообщения. """


class NewDealEvent(BaseEvent):
    """
    Класс события: новая созданная сделка (когда покупатель оплатил предмет).

    :param deal: Объект новой сделки.
    :type deal: `PlayerokAPI.types.ItemDeal`

    :param chat: Объект чата, в котором произошло событие.
    :type chat: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal: types.ItemDeal, chat: types.Chat):
        super(NewDealEvent, self).__init__(EventTypes.NEW_DEAL, chat)
        self.deal: types.ItemDeal = deal
        """ Объект сделки. """


class NewReviewEvent(BaseEvent):
    """
    Класс события: новый отзыв от покупателя.

    :param deal: Объект сделки с отзывом.
    :type deal: `PlayerokAPI.types.ItemDeal`

    :param chat: Объект чата, в котором произошло событие.
    :type chat: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal: types.ItemDeal, chat: types.Chat):
        super(NewReviewEvent, self).__init__(EventTypes.NEW_REVIEW, chat)
        self.deal: types.ItemDeal = deal
        """ Объект сделки. """


class DealConfirmedEvent(BaseEvent):
    """
    Класс события: покупатель подтвердил сделку.

    :param deal: Объект сделки.
    :type deal: `PlayerokAPI.types.ItemDeal`

    :param chat: Объект чата, в котором произошло событие.
    :type chat: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal: types.ItemDeal, chat: types.Chat):
        super(DealConfirmedEvent, self).__init__(EventTypes.DEAL_CONFIRMED, chat)
        self.deal: types.ItemDeal = deal
        """ Объект сделки. """


class DealRolledBackEvent(BaseEvent):
    """
    Класс события: продавец вернул средства за сделку.

    :param deal: Объект сделки.
    :type deal: `PlayerokAPI.types.ItemDeal`

    :param chat: Объект чата, в котором произошло событие.
    :type chat: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal: types.ItemDeal, chat: types.Chat):
        super(DealRolledBackEvent, self).__init__(EventTypes.DEAL_ROLLED_BACK, chat)
        self.deal: types.ItemDeal = deal
        """ Объект сделки. """


class DealHasProblemEvent(BaseEvent):
    """
    Класс события: кто-то сообщил о проблеме в сделке.

    :param deal: Объект сделки.
    :type deal: `PlayerokAPI.types.ItemDeal`

    :param chat: Объект чата, в котором произошло событие.
    :type chat: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal: types.ItemDeal, chat: types.Chat):
        super(DealHasProblemEvent, self).__init__(EventTypes.DEAL_HAS_PROBLEM, chat)
        self.deal: types.ItemDeal = deal
        """ Объект сделки. """


class DealProblemResolvedEvent(BaseEvent):
    """
    Класс события: проблема в сделке решена.

    :param deal: Объект сделки.
    :type deal: `PlayerokAPI.types.ItemDeal`

    :param chat: Объект чата, в котором произошло событие.
    :type chat: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal: types.ItemDeal, chat: types.Chat):
        super(DealProblemResolvedEvent, self).__init__(
            EventTypes.DEAL_PROBLEM_RESOLVED, chat
        )
        self.deal: types.ItemDeal = deal
        """ Объект сделки. """


class DealStatusChangedEvent(BaseEvent):
    """
    Класс события: статус сделки изменён.

    :param deal: Объект сделки.
    :type deal: `PlayerokAPI.types.ItemDeal`

    :param chat: Объект чата, в котором произошло событие.
    :type chat: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal: types.ItemDeal, chat: types.Chat):
        super(DealStatusChangedEvent, self).__init__(
            EventTypes.DEAL_STATUS_CHANGED, chat
        )
        self.deal: types.ItemDeal = deal
        """ Объект сделки. """


class ItemPaidEvent(BaseEvent):
    """
    Класс события: предмет оплачен.

    :param deal: Объект сделки.
    :type deal: `PlayerokAPI.types.Item`

    :param chat: Объект чата, в котором произошло событие.
    :type chat: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal: types.ItemDeal, chat: types.Chat):
        super(ItemPaidEvent, self).__init__(EventTypes.ITEM_PAID, chat)
        self.deal: types.ItemDeal = deal
        """ Объект сделки. """


class ItemSentEvent(BaseEvent):
    """
    Класс события: предмет отправлен покупателю.

    :param deal: Объект сделки.
    :type deal: `PlayerokAPI.types.Item`

    :param chat: Объект чата, в котором произошло событие.
    :type chat: `PlayerokAPI.types.Chat`
    """

    def __init__(self, deal: types.ItemDeal, chat: types.Chat):
        super(ItemSentEvent, self).__init__(EventTypes.ITEM_SENT, chat)
        self.deal: types.ItemDeal = deal
        """ Объект Сделки. """