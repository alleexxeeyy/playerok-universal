from ..account import Account
from ..types import ChatList, ChatMessage, Chat
from .events import *
from typing import Generator

import time

class EventListener:
    """
    Слушатель событий с Playerok.com.

    :param account: Объект аккаунта.
    :type account: `PlayerokAPI.account.Account`
    """
    
    def __init__(self, account: Account):
        self.account: Account = account
        """ Объект аккаунта. """

    def parse_chat_event(self, chat: Chat) -> list[ChatInitializedEvent]:
        """
        Получает ивент с чата.

        :param chat: Объект чата.
        :type chat: `PlayerokAPI.types.Chat`

        :return: Массив ивентов.
        :rtype: `list` of
        `PlayerokAPI.listener.events.ChatInitializedEvent`
        """
        
        if chat:
            return [ChatInitializedEvent(chat)]
        return []

    def get_chat_events(self, chats: ChatList):
        """
        Получает новые ивенты чатов.
        
        :param chats: Страница чатов.
        :type chats: `PlayerokAPI.types.ChatList`

        :return: Массив новых ивентов.
        :rtype: `list` of
        `PlayerokAPI.listener.events.ChatInitializedEvent`
        """

        events = []
        for chat in chats.chats:
            this_events = self.parse_chat_event(chat=chat)
            for event in this_events:
                events.append(event)
        return events

    def parse_message_event(self, message: ChatMessage) -> list[NewMessageEvent | NewDealEvent | ItemPaidEvent
                                                                | ItemSentEvent | DealConfirmedEvent | DealRolledBackEvent | DealHasProblemEvent
                                                                | DealProblemResolvedEvent | DealStatusChangedEvent]:
        """
        Получает ивент с сообщения.
        
        :param message: Объект сообщения.
        :type message: `PlayerokAPI.types.ChatMessage`

        :return: Массив ивентов.
        :rtype: `list` of 
        `PlayerokAPI.listener.events.ChatInitializedEvent` \
        _or_ `PlayerokAPI.listener.events.NewMessageEvent` \
        _or_ `PlayerokAPI.listener.events.NewDealEvent` \
        _or_ `PlayerokAPI.listener.events.ItemPaidEvent` \
        _or_ `PlayerokAPI.listener.events.ItemSentEvent` \
        _or_ `PlayerokAPI.listener.events.DealConfirmedEvent` \
        _or_ `PlayerokAPI.listener.events.DealRolledBackEvent` \
        _or_ `PlayerokAPI.listener.events.DealHasProblemEvent` \
        _or_ `PlayerokAPI.listener.events.DealProblemResolvedEvent` \
        _or_ `PlayerokAPI.listener.events.DealStatusChangedEvent(message.deal)`
        """
        
        if not message:
            return []
        if message.text == "{{ITEM_PAID}}" and message.deal is not None:
            return [NewDealEvent(message.deal), ItemPaidEvent(message.deal)]
        elif message.text == "{{ITEM_SENT}}" and message.deal is not None:
            return [ItemSentEvent(message.deal)]
        elif message.text == "{{DEAL_CONFIRMED}}" and message.deal is not None:
            return [DealConfirmedEvent(message.deal), DealStatusChangedEvent(message.deal)]
        elif message.text == "{{DEAL_ROLLED_BACK}}" and message.deal is not None:
            return [DealRolledBackEvent(message.deal), DealStatusChangedEvent(message.deal)]
        elif message.text == "{{DEAL_HAS_PROBLEM}}" and message.deal is not None:
            return [DealHasProblemEvent(message.deal), DealStatusChangedEvent(message.deal)]
        elif message.text == "{{DEAL_PROBLEM_RESOLVED}}" and message.deal is not None:
            return [DealProblemResolvedEvent(message.deal), DealStatusChangedEvent(message.deal)]
        
        return [NewMessageEvent(message)]

    def get_message_events(self, old_chats: ChatList, new_chats: ChatList):
        """
        Получает новые ивенты сообщений, сравнивая старые чаты с новыми полученными.
        
        :param old_chats: Старые чаты.
        :type old_chats: `PlayerokAPI.types.ChatList`
        
        :param new_chats: Новые чаты.
        :type new_chats: `PlayerokAPI.types.ChatList`

        :return: Массив новых ивентов.
        :rtype: `list` of 
        `PlayerokAPI.listener.events.ChatInitializedEvent` \
        _or_ `PlayerokAPI.listener.events.NewMessageEvent` \
        _or_ `PlayerokAPI.listener.events.NewDealEvent` \
        _or_ `PlayerokAPI.listener.events.ItemPaidEvent` \
        _or_ `PlayerokAPI.listener.events.ItemSentEvent` \
        _or_ `PlayerokAPI.listener.events.DealConfirmedEvent` \
        _or_ `PlayerokAPI.listener.events.DealRolledBackEvent` \
        _or_ `PlayerokAPI.listener.events.DealHasProblemEvent` \
        _or_ `PlayerokAPI.listener.events.DealProblemResolvedEvent` \
        _or_ `PlayerokAPI.listener.events.DealStatusChangedEvent(message.deal)`
        """
        
        events = []
        old_chat_map = {chat.id: chat for chat in old_chats.chats}
        for new_chat in new_chats.chats:
            old_chat = old_chat_map.get(new_chat.id)
            
            if not old_chat:
                msg_list = self.account.get_chat_messages(new_chat.id, 5)
                for msg in reversed(msg_list.messages):
                    events.extend(self.parse_message_event(msg))
                continue

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

            for msg in reversed(new_msgs):
                events.extend(self.parse_message_event(msg))
        return events      
                
    def listen(self, requests_delay: int | float = 4) -> Generator[ChatInitializedEvent | NewMessageEvent | NewDealEvent | ItemPaidEvent
                                                                  | ItemSentEvent | DealConfirmedEvent | DealRolledBackEvent | DealHasProblemEvent
                                                                  | DealProblemResolvedEvent | DealStatusChangedEvent,
                                                                  None, None]:
        """
        "Слушает" события в чатах. 
        Бесконечно отправляет запросы, узнавая новые события из чатов.

        :param requests_delay: Периодичность отправления запросов (в секундах).
        :type requests_delay: `int` or `float`

        :return: Полученный ивент.
        :rtype: `Generator` of
        `PlayerokAPI.listener.events.ChatInitializedEvent` \
        _or_ `PlayerokAPI.listener.events.NewMessageEvent` \
        _or_ `PlayerokAPI.listener.events.NewDealEvent` \
        _or_ `PlayerokAPI.listener.events.ItemPaidEvent` \
        _or_ `PlayerokAPI.listener.events.ItemSentEvent` \
        _or_ `PlayerokAPI.listener.events.DealConfirmedEvent` \
        _or_ `PlayerokAPI.listener.events.DealRolledBackEvent` \
        _or_ `PlayerokAPI.listener.events.DealHasProblemEvent` \
        _or_ `PlayerokAPI.listener.events.DealProblemResolvedEvent` \
        _or_ `PlayerokAPI.listener.events.DealStatusChangedEvent(message.deal)`
        """

        chats: ChatList | None = None
        while True:
            try:
                next_chats = self.account.get_chats(10)
                if not chats:
                    events = self.get_chat_events(next_chats)
                    for event in events:
                        yield event
                elif chats != next_chats:
                    events = self.get_message_events(chats, next_chats)
                    for event in events:
                        yield event

                chats = next_chats
                time.sleep(requests_delay)
            except Exception as e:
                print(f"Ошибка при получении ивентов: {e}")
                time.sleep(requests_delay)  
                continue
