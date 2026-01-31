from typing import Generator
from logging import getLogger
from datetime import datetime

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
        self.__review_check_deals: list[str] = [] # [deal_id]
        self.__last_check_time: dict[str, datetime] = {} # {deal_id: last_check_time}
        
        self.__listened_messages: list[str] = [] # [mess_id]
        self.__saved_deals: list[str] = [] # [deal_id]

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

    def parse_message_events(
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
            if message.deal.id not in self.__saved_deals:
                self.__saved_deals.append(message.deal.id)
                return [
                    NewDealEvent(message.deal, chat), 
                    ItemPaidEvent(message.deal, chat)
                ]
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
    
    def _correct_isodate(
        self, iso_date: str
    ) -> datetime:
        return datetime.fromisoformat(iso_date.replace("Z", "+00:00"))

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
        | DealStatusChangedEvent
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

        if get_new_review_events:
            for deal_id in self.__review_check_deals:
                if not self._should_check_deal(deal_id):
                    continue
                deal = self.account.get_deal(deal_id)
                if deal.review is not None:
                    del self.__review_check_deals[self.__review_check_deals.index(deal_id)]
                    try: deal.chat = self.account.get_chat(deal.chat.id)
                    except: pass
                    events.append(NewReviewEvent(deal, deal.chat))
        
        old_chats_last_mess_ids = [chat.last_message.id for chat in old_chats.chats if chat.last_message] if old_chats else []
        new_chats_last_mess_ids = [chat.last_message.id for chat in new_chats.chats if chat.last_message] if new_chats else []
        if old_chats_last_mess_ids != new_chats_last_mess_ids:
            old_chat_map = {chat.id: chat for chat in old_chats.chats}
            for new_chat in new_chats.chats:
                old_chat = old_chat_map.get(new_chat.id)

                if not old_chat:
                    time.sleep(2)
                    msg_list = self.account.get_chat_messages(new_chat.id, 24)
                    new_msgs = [msg for msg in msg_list.messages]
                elif old_chat:
                    if not new_chat.last_message or not old_chat.last_message:
                        continue
                    if new_chat.last_message.id == old_chat.last_message.id:
                        continue
                    time.sleep(2) # ебучая задержка, потому что плеерок не сразу отображает новые сообщения в запросе
                    msg_list = self.account.get_chat_messages(new_chat.id, 24)
                    new_msgs = [
                        msg for msg in msg_list.messages 
                        if self._correct_isodate(msg.created_at) > self._correct_isodate(old_chat.last_message.created_at)
                    ]
                    if new_chat.last_message.id not in [msg.id for msg in new_msgs]:
                        new_msgs.append(new_chat.last_message)
                    #new_msgs = [new_chat.last_message]

                for msg in sorted(new_msgs, key=lambda m: m.created_at):
                    if msg.id in self.__listened_messages:
                        continue
                    if get_new_review_events and msg.deal and msg.deal.id not in self.__review_check_deals:
                        self.__review_check_deals.append(msg.deal.id)
                    self.__listened_messages.append(msg.id)
                    events.extend(self.parse_message_events(msg, new_chat))
        
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
        None
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
                next_chats = self.account.get_chats(24)
                if not chats:
                    events = self.get_chat_events(next_chats)
                    for event in events:
                        yield event
                else:
                    events = self.get_message_events(chats, next_chats, get_new_review_events)
                    for event in events:
                        yield event
                chats = next_chats
            except Exception as e:
                self.__logger.error(f"Ошибка при получении ивентов: {e}")
            time.sleep(requests_delay)
