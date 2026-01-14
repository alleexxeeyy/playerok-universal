import json
import uuid
import time
from logging import getLogger
from typing import Generator
from threading import Thread
from queue import Queue

import websocket
import ssl

from ..account import Account
from ..types import (
    ChatMessage, 
    Chat
)
from ..parser import (
    chat, 
    chat_message
)
from ..misc import QUERIES
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

        self.chat_subscriptions = {}
        self.review_check_deals = []
        self.deal_checks = {}
        self.chats = []
        self.logger = getLogger("playerokapi.listener")

    def _get_actual_message(
        self, message_id: str, chat_id: str
    ):
        time.sleep(4) # задержка, так как playerok не позволяет получать новые сообщения слишком быстро
        msg_list = self.account.get_chat_messages(chat_id, count=12)
        try: msg = [msg for msg in msg_list.messages if msg.id == message_id][0]
        except: return
        return msg
    
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
        if not message:
            return []
        
        if message.text == "{{ITEM_PAID}}":
            actual_msg = self._get_actual_message(message.id, chat.id)
            if actual_msg and actual_msg.deal is not None:
                if actual_msg.deal.id not in self.review_check_deals:
                    self.review_check_deals.append(actual_msg.deal.id)
                return [
                    NewDealEvent(actual_msg.deal, chat), 
                    ItemPaidEvent(actual_msg.deal, chat)
                ]
        
        elif message.text == "{{ITEM_SENT}}":
            actual_msg = self._get_actual_message(message.id, chat.id)
            if actual_msg and actual_msg.deal is not None:
                return [ItemSentEvent(actual_msg.deal, chat)]
        
        elif message.text == "{{DEAL_CONFIRMED}}":
            actual_msg = self._get_actual_message(message.id, chat.id)
            if actual_msg and actual_msg.deal is not None:
                return [
                    DealConfirmedEvent(actual_msg.deal, chat),
                    DealStatusChangedEvent(actual_msg.deal, chat),
                ]
        
        elif message.text == "{{DEAL_ROLLED_BACK}}":
            actual_msg = self._get_actual_message(message.id, chat.id)
            if actual_msg and actual_msg.deal is not None:
                return [
                    DealRolledBackEvent(actual_msg.deal, chat),
                    DealStatusChangedEvent(actual_msg.deal, chat),
                ]
        
        elif message.text == "{{DEAL_HAS_PROBLEM}}":
            actual_msg = self._get_actual_message(message.id, chat.id)
            if actual_msg and actual_msg.deal is not None:
                return [
                    DealHasProblemEvent(actual_msg.deal, chat),
                    DealStatusChangedEvent(actual_msg.deal, chat),
                ]
        
        elif message.text == "{{DEAL_PROBLEM_RESOLVED}}":
            actual_msg = self._get_actual_message(message.id, chat.id)
            if actual_msg and actual_msg.deal is not None:
                return [
                    DealProblemResolvedEvent(actual_msg.deal, chat),
                    DealStatusChangedEvent(actual_msg.deal, chat),
                ]

        return [NewMessageEvent(message, chat)]
    
    def _send_connection_init(self, ws):
        ws.send(json.dumps({
            "type": "connection_init", 
            "payload": {
                "x-gql-op": "ws-subscription",
                "x-gql-path": "/self.chats/[id]",
                "x-timezone-offset": -180
            }
        }))

    def _subscribe_chat_updated(self, ws):
        ws.send(json.dumps({
            "id": str(uuid.uuid4()), 
            "payload": {
                "extensions": {},
                "operationName": "chatUpdated",
                "query": QUERIES.get("chatUpdated"),
                "variables": {
                    "filter": {
                        "userId": self.account.id
                    },
                    "showForbiddenImage": True
                }
            },
            "type": "subscribe"
        }))

    def _subscribe_chat_marked_as_read(self, ws):
        ws.send(json.dumps({
            "id": str(uuid.uuid4()), 
            "payload": {
                "extensions": {},
                "operationName": "chatMarkedAsRead",
                "query": QUERIES.get("chatMarkedAsRead"),
                "variables": {
                    "filter": {
                        "userId": self.account.id
                    },
                    "showForbiddenImage": True
                }
            },
            "type": "subscribe"
        }))

    def _subscribe_user_updated(self, ws):
        ws.send(json.dumps({
            "id": str(uuid.uuid4()), 
            "payload": {
                "extensions": {},
                "operationName": "userUpdated",
                "query": QUERIES.get("userUpdated"),
                "variables": {
                    "userId": self.account.id
                }
            },
            "type": "subscribe"
        }))

    def _subscribe_chat_message_created(self, ws, chat_id):
        _uuid = str(uuid.uuid4())
        self.chat_subscriptions[_uuid] = chat_id
        ws.send(json.dumps({
            "id": _uuid, 
            "payload": {
                "extensions": {},
                "operationName": "chatMessageCreated",
                "query": QUERIES.get("chatMessageCreated"),
                "variables": {
                    "filter": {
                        "chatId": chat_id
                    }
                }
            },
            "type": "subscribe"
        }))

    def _is_chat_subscribed(self, chat_id):
        for _, sub_chat_id in self.chat_subscriptions.items():
            if chat_id == sub_chat_id:
                return True
        return False
        
    def listen_new_messages(self):
        headers = {
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "connection": "Upgrade",
            "origin": "https://playerok.com",
            "pragma": "no-cache",
            "sec-websocket-extensions": "permessage-deflate; client_max_window_bits",
            "cookie": f"token={self.account.token}",
            "user-agent": self.account.user_agent
        }

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.load_default_certs()
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3

        chat_list = self.account.get_chats(count=24) # инициализация первых 24 чатов
        self.chats = [chat for chat in chat_list.chats]
        for chat_ in self.chats:
            yield ChatInitializedEvent(chat_)

        ws = websocket.WebSocket(
            sslopt={"context": ssl_context}
        )
        ws.connect(
            url="wss://ws.playerok.com/graphql",
            header=[f"{k}: {v}" for k, v in headers.items()],
            subprotocols=["graphql-transport-ws"]
        )

        self._send_connection_init(ws)          

        while True:
            msg = ws.recv()
            msg_data = json.loads(msg)
            self.logger.debug(f"websocket msg received: {msg_data}")
            
            if msg_data["type"] == "connection_ack":
                self._subscribe_chat_updated(ws)
                for chat_ in self.chats:
                    self._subscribe_chat_message_created(ws, chat_.id)
            
            else:
                if "chatUpdated" in msg_data["payload"]["data"]:
                    _chat = chat(msg_data["payload"]["data"]["chatUpdated"])
                    _message = chat_message(msg_data["payload"]["data"]["chatUpdated"]["lastMessage"])
                    
                    already_subscribed = self._is_chat_subscribed(_chat.id)
                    is_new_chat = _chat.id not in [chat_.id for chat_ in self.chats]

                    if is_new_chat:
                        self.chats.append(_chat)
                    if not already_subscribed:
                        self._subscribe_chat_message_created(ws, _chat.id)
                    else:
                        for old_chat in self.chats:
                            if old_chat.id == _chat.id:
                                self.chats.remove(old_chat)
                                self.chats.append(_chat)
                                break
                    
                    if not already_subscribed: # если ещё не были подписаны на чат - получаем новое сообщение в этом ивенте
                        events = []
                        if is_new_chat:
                            events.append(ChatInitializedEvent(_chat))
                        events.extend(self.parse_message_events(_message, _chat))
                        for event in events:
                            yield event
                    # иначе, если уже подписаны на чат - получаем сообщение из chatMessageCreated

                if "chatMessageCreated" in msg_data["payload"]["data"]:
                    chat_id = self.chat_subscriptions.get(msg_data["id"])
                    try: _chat = [chat_ for chat_ in self.chats if chat_.id == chat_id][0]
                    except: continue
                    _message = chat_message(msg_data["payload"]["data"]["chatMessageCreated"])

                    events = self.parse_message_events(_message, _chat)
                    for event in events:
                        yield event

    def _should_check_deal(self, deal_id, delay=30) -> bool:
        now = time.time()
        info = self.deal_checks.get(deal_id, {"last": 0, "tries": 0})
        last_time = info["last"]
        tries = info["tries"]
        
        if now - last_time > delay:
            self.deal_checks[deal_id] = {
                "last": now,
                "tries": tries+1
            }
            return True
        elif tries >= 30:
            if deal_id in self.review_check_deals:
                self.review_check_deals.remove(deal_id)
            del self.deal_checks[deal_id]

        return False
    
    def listen_new_reviews(self):
        while True:
            for deal_id in list(self.review_check_deals):
                if not self._should_check_deal(deal_id):
                    continue
                deal = self.account.get_deal(deal_id)
                
                if deal.review is not None:
                    if deal_id in self.review_check_deals:
                        self.review_check_deals.remove(deal_id)
                    
                    try: deal.chat = [chat_ for chat_ in self.chats if chat_.id == getattr(getattr(deal, "chat"), "id")][0]
                    except: 
                        try: deal.chat = self.account.get_chat(deal.chat.id)
                        except: pass
                    
                    yield NewReviewEvent(deal, deal.chat)
            time.sleep(1)

    def listen(
        self, 
        get_new_message_events: bool = True,
        get_new_review_events: bool = True
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
        if not any([get_new_review_events, get_new_message_events]):
            return
        
        q = Queue()

        def run(gen):
            for event in gen:
                q.put(event)

        if get_new_message_events:
            Thread(target=run, args=(self.listen_new_messages(),), daemon=True).start()
        if get_new_review_events:
            Thread(target=run, args=(self.listen_new_reviews(),), daemon=True).start()

        while True:
            yield q.get()