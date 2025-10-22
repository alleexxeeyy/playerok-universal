from typing import Generator
from logging import getLogger
import time

from ..account import Account
from ..types import ChatList, ChatMessage, Chat
from .events import *


class EventListener:
    """
    Слушатель событий с Playerok.com.

    :param account: Объект аккаунта.
    :type account: `playerokapi.account.Account`
    """

    def __init__(self, account: Account):
        self.account: Account = account
        """ Объект аккаунта. """

        self.__logger = getLogger("playerokapi.listener")
        self.__review_check_deals: dict = {} # {deal_id: last_known_testimonial_id}
        self.__last_check_time: dict = {} # {deal_id: last_check_time}

    def parse_chat_event(
        self, chat: Chat
    ) -> list[ChatInitializedEvent]:
        """
        Получает ивент с чата.

        :param chat: Объект чата.
        :type chat: `playerokapi.types.Chat`

        :return: Массив ивентов.
        :rtype: `list` of
        `playerokapi.listener.events.ChatInitializedEvent`
        """

        if chat:
            return [ChatInitializedEvent(chat)]
        return []

    def get_chat_events(
        self, chats: ChatList
    ) -> list[ChatInitializedEvent]:
        """
        Получает новые ивенты чатов.

        :param chats: Страница чатов.
        :type chats: `playerokapi.types.ChatList`

        :return: Массив новых ивентов.
        :rtype: `list` of
        `playerokapi.listener.events.ChatInitializedEvent`
        """

        events = []
        for chat in chats.chats:
            this_events = self.parse_chat_event(chat=chat)
            for event in this_events:
                events.append(event)
        return events

    def parse_message_event(
        self, message: ChatMessage, chat: Chat
    ) -> list[
        NewMessageEvent
        | NewDealEvent
        | ItemPaidEvent
        | ItemSentEvent
        | DealConfirmedEvent
        | DealRolledBackEvent
        | DealHasProblemEvent
        | DealProblemResolvedEvent
        | DealStatusChangedEvent
    ]:
        """
        Получает ивент с сообщения.
        
        :param message: Объект сообщения.
        :type message: `playerokapi.types.ChatMessage`

        :return: Массив ивентов.
        :rtype: `list` of 
        `playerokapi.listener.events.ChatInitializedEvent` \
        _or_ `playerokapi.listener.events.NewMessageEvent` \
        _or_ `playerokapi.listener.events.NewDealEvent` \
        _or_ `playerokapi.listener.events.ItemPaidEvent` \
        _or_ `playerokapi.listener.events.ItemSentEvent` \
        _or_ `playerokapi.listener.events.DealConfirmedEvent` \
        _or_ `playerokapi.listener.events.DealRolledBackEvent` \
        _or_ `playerokapi.listener.events.DealHasProblemEvent` \
        _or_ `playerokapi.listener.events.DealProblemResolvedEvent` \
        _or_ `playerokapi.listener.events.DealStatusChangedEvent(message.deal)`
        """

        if not message:
            return []
        if message.text == "{{ITEM_PAID}}" and message.deal is not None:
            return [NewDealEvent(message.deal, chat), ItemPaidEvent(message.deal, chat)]
        elif message.text == "{{ITEM_SENT}}" and message.deal is not None:
            return [ItemSentEvent(message.deal, chat)]
        elif message.text == "{{DEAL_CONFIRMED}}" and message.deal is not None:
            return [
                DealConfirmedEvent(message.deal, chat),
                DealStatusChangedEvent(message.deal, chat),
            ]
        elif message.text == "{{DEAL_ROLLED_BACK}}" and message.deal is not None:
            return [
                DealRolledBackEvent(message.deal, chat),
                DealStatusChangedEvent(message.deal, chat),
            ]
        elif message.text == "{{DEAL_HAS_PROBLEM}}" and message.deal is not None:
            return [
                DealHasProblemEvent(message.deal, chat),
                DealStatusChangedEvent(message.deal, chat),
            ]
        elif message.text == "{{DEAL_PROBLEM_RESOLVED}}" and message.deal is not None:
            return [
                DealProblemResolvedEvent(message.deal, chat),
                DealStatusChangedEvent(message.deal, chat),
            ]

        return [NewMessageEvent(message, chat)]

    def _should_check_deal(
        self, deal_id: int, delay: int = 30
    ) -> bool:
        now = time.time()
        last_time = self.__last_check_time.get(deal_id, 0)
        if now - last_time > delay:
            self.__last_check_time[deal_id] = now
            return True
        return False

    def _check_for_new_review(
        self, chat: Chat
    ) -> NewReviewEvent | None:
        deal_id = chat.last_message.deal.id
        # проверка раз в N минут, или только если прошло время, или если что-то изменилось
        if not self._should_check_deal(deal_id):
            return
        deal = self.account.get_deal(deal_id)
        if deal.review is not None:
            del self.__review_check_deals[deal_id]
            return NewReviewEvent(deal, chat)

    def get_message_events(
        self, old_chats: ChatList, new_chats: ChatList, get_new_review_events: bool
    ) -> list[
        NewMessageEvent
        | NewDealEvent
        | NewReviewEvent
        | ItemPaidEvent
        | ItemSentEvent
        | DealConfirmedEvent
        | DealRolledBackEvent
        | DealHasProblemEvent
        | DealProblemResolvedEvent
        | DealStatusChangedEvent,
    ]:
        """
        Получает новые ивенты сообщений, сравнивая старые чаты с новыми полученными.
        
        :param old_chats: Старые чаты.
        :type old_chats: `playerokapi.types.ChatList`
        
        :param new_chats: Новые чаты.
        :type new_chats: `playerokapi.types.ChatList`

        :return: Массив новых ивентов.
        :rtype: `list` of 
        `playerokapi.listener.events.ChatInitializedEvent` \
        _or_ `playerokapi.listener.events.NewMessageEvent` \
        _or_ `playerokapi.listener.events.NewDealEvent` \
        _or_ `playerokapi.listener.events.NewReviewEvent` \
        _or_ `playerokapi.listener.events.ItemPaidEvent` \
        _or_ `playerokapi.listener.events.ItemSentEvent` \
        _or_ `playerokapi.listener.events.DealConfirmedEvent` \
        _or_ `playerokapi.listener.events.DealRolledBackEvent` \
        _or_ `playerokapi.listener.events.DealHasProblemEvent` \
        _or_ `playerokapi.listener.events.DealProblemResolvedEvent` \
        _or_ `playerokapi.listener.events.DealStatusChangedEvent(message.deal)`
        """

        events = []
        old_chat_map = {chat.id: chat for chat in old_chats.chats}
        for new_chat in new_chats.chats:
            old_chat = old_chat_map.get(new_chat.id)

            if not old_chat:
                # если это новый чат, парсим ивенты только последнего сообщения, ведь это - покупка товара
                events.extend(self.parse_message_event(new_chat.last_message, new_chat))
                continue

            if (
                get_new_review_events 
                and new_chat.last_message.deal 
                and old_chat.last_message.deal
                and new_chat.last_message.deal.id in self.__review_check_deals
            ):
                new_review_event = self._check_for_new_review(new_chat)
                if new_review_event: events.append(new_review_event)

            if not new_chat.last_message or not old_chat.last_message:
                continue
            if new_chat.last_message.id == old_chat.last_message.id:
                continue

            msg_list = self.account.get_chat_messages(new_chat.id, 10)
            new_msgs = []
            for msg in msg_list.messages:
                if msg.id == old_chat.last_message.id:
                    break
                new_msgs.append(msg)

            if get_new_review_events and new_chat.last_message.deal:
                self.__review_check_deals[new_chat.last_message.deal.id] = None

            for msg in reversed(new_msgs):
                events.extend(self.parse_message_event(msg, new_chat))
        return events

    def listen(
        self, requests_delay: int | float = 4, get_new_review_events: bool = True
    ) -> Generator[
        ChatInitializedEvent
        | NewMessageEvent
        | NewDealEvent
        | NewReviewEvent
        | ItemPaidEvent
        | ItemSentEvent
        | DealConfirmedEvent
        | DealRolledBackEvent
        | DealHasProblemEvent
        | DealProblemResolvedEvent
        | DealStatusChangedEvent,
        None,
        None,
    ]:
        """
        "Слушает" события в чатах. 
        Бесконечно отправляет запросы, узнавая новые события из чатов.

        :param requests_delay: Периодичность отправления запросов (в секундах).
        :type requests_delay: `int` or `float`

        :param get_new_review_events: Нужно ли слушать новые отзывы? (отправляет больше запросов).
        :type get_new_review_events: `bool`

        :return: Полученный ивент.
        :rtype: `Generator` of
        `playerokapi.listener.events.ChatInitializedEvent` \
        _or_ `playerokapi.listener.events.NewMessageEvent` \
        _or_ `playerokapi.listener.events.NewDealEvent` \
        _or_ `playerokapi.listener.events.NewReviewEvent` \
        _or_ `playerokapi.listener.events.ItemPaidEvent` \
        _or_ `playerokapi.listener.events.ItemSentEvent` \
        _or_ `playerokapi.listener.events.DealConfirmedEvent` \
        _or_ `playerokapi.listener.events.DealRolledBackEvent` \
        _or_ `playerokapi.listener.events.DealHasProblemEvent` \
        _or_ `playerokapi.listener.events.DealProblemResolvedEvent` \
        _or_ `playerokapi.listener.events.DealStatusChangedEvent(message.deal)`
        """

        chats: ChatList = None
        while True:
            try:
                next_chats = self.account.get_chats(10)
                if not chats:
                    events = self.get_chat_events(next_chats)
                    for event in events:
                        yield event
                elif chats != next_chats:
                    events = self.get_message_events(chats, next_chats, get_new_review_events)
                    for event in events:
                        yield event

                chats = next_chats
                time.sleep(requests_delay)
            except Exception as e:
                self.__logger.error(f"Ошибка при получении ивентов: {e}")
                time.sleep(requests_delay)
                continue
