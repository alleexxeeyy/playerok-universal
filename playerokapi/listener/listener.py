import json
import uuid
import time
import traceback
from datetime import datetime
from logging import getLogger
from typing import Generator
from threading import Thread
from queue import Queue
from threading import Event as ThreadingEvent

import websocket

from ..account import Account
from ..types import (
    ChatMessage, 
    Chat,
    ItemDeal
)
from ..enums import ChatTypes
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

        self.chat_subscriptions = {}
        self.review_check_deals = []
        self.review_deal_times = {}
        self.chats = []
        self.processed_deals = []
        self.active_deals = {} # chat_id: [(deal_id, last_status, status_date), ...]
        self.last_st_deal_times = {}
        self.ws = None
        self.q = None

        self._possible_new_chat = ThreadingEvent()
        self._last_chat_check = 0

        self.logger = getLogger("playerokapi.listener")

    def _get_actual_message(
        self, message_id: str, chat_id: str
    ):
        for _ in range(3):
            time.sleep(4)
            try: msg_list = self.account.get_chat_messages(chat_id, count=12)
            except: return
            try: return [msg for msg in msg_list.messages if msg.id == message_id][0]
            except: pass

    """def _set_active_deal(
        self, chat: Chat, deal: ItemDeal, status_date: datetime
    ):
        if chat.id not in self.active_deals:
            self.active_deals[chat.id] = []
        
        try: deal_tuple = [tuple for tuple in self.active_deals[chat.id] if deal.id in tuple][0]
        except: deal_tuple = ()
        
        if not deal_tuple:
            self.active_deals[chat.id].append((deal.id, deal.status, status_date))
        else:
            indx = self.active_deals[chat.id].index(deal_tuple)
            self.active_deals[chat.id][indx] = (deal.id, deal.status, status_date)"""
    
    def _parse_message_events(
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
            actual_msg = self._get_actual_message(message.id, chat.id) or message
            if actual_msg and actual_msg.deal:
                deal_id = actual_msg.deal.id
                #status_date = datetime.fromisoformat(actual_msg.created_at)
                #self._set_active_deal(chat, actual_msg.deal, status_date)
                if deal_id not in self.review_check_deals:
                    self.review_check_deals.append(deal_id)
                if deal_id not in self.processed_deals:
                    self.processed_deals.append(deal_id)
                else:
                    return []
                return [
                    NewDealEvent(actual_msg.deal, chat), 
                    ItemPaidEvent(actual_msg.deal, chat)
                ]
        
        elif message.text == "{{ITEM_SENT}}":
            actual_msg = self._get_actual_message(message.id, chat.id) or message
            if actual_msg and actual_msg.deal:
                #status_date = datetime.fromisoformat(actual_msg.created_at)
                #self._set_active_deal(chat, actual_msg.deal, status_date)
                return [
                    ItemSentEvent(actual_msg.deal, chat),
                    DealStatusChangedEvent(actual_msg.deal, chat)
                ]
        
        elif message.text == "{{DEAL_CONFIRMED}}":
            actual_msg = self._get_actual_message(message.id, chat.id) or message
            if actual_msg and actual_msg.deal:
                status_date = datetime.fromisoformat(actual_msg.created_at)
                ##self._set_active_deal(chat, actual_msg.deal, status_date)
                return [
                    DealConfirmedEvent(actual_msg.deal, chat),
                    DealStatusChangedEvent(actual_msg.deal, chat),
                ]
        
        elif message.text == "{{DEAL_ROLLED_BACK}}":
            actual_msg = self._get_actual_message(message.id, chat.id) or message
            if actual_msg and actual_msg.deal:
                #status_date = datetime.fromisoformat(actual_msg.created_at)
                #self._set_active_deal(chat, actual_msg.deal, status_date)
                return [
                    DealRolledBackEvent(actual_msg.deal, chat),
                    DealStatusChangedEvent(actual_msg.deal, chat),
                ]
        
        elif message.text == "{{DEAL_HAS_PROBLEM}}":
            actual_msg = self._get_actual_message(message.id, chat.id) or message
            if actual_msg and actual_msg.deal:
                #status_date = datetime.fromisoformat(actual_msg.created_at)
                #self._set_active_deal(chat, actual_msg.deal, status_date)
                return [
                    DealHasProblemEvent(actual_msg.deal, chat),
                    DealStatusChangedEvent(actual_msg.deal, chat),
                ]
        
        elif message.text == "{{DEAL_PROBLEM_RESOLVED}}":
            actual_msg = self._get_actual_message(message.id, chat.id) or message
            if actual_msg and actual_msg.deal:
                #status_date = datetime.fromisoformat(actual_msg.created_at)
                #self._set_active_deal(chat, actual_msg.deal, status_date)
                return [
                    DealProblemResolvedEvent(actual_msg.deal, chat),
                    DealStatusChangedEvent(actual_msg.deal, chat),
                ]

        return [NewMessageEvent(message, chat)]
    
    def _send_connection_init(self):
        self.ws.send(json.dumps({
            "type": "connection_init", 
            "payload": {
                "x-gql-op": "ws-subscription",
                "x-gql-path": "/self.chats/[id]",
                "x-timezone-offset": -180
            }
        }))

    def _subscribe_chat_updated(self):
        self.ws.send(json.dumps({
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

    def _subscribe_chat_marked_as_read(self):
        self.ws.send(json.dumps({
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

    def _subscribe_user_updated(self):
        self.ws.send(json.dumps({
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

    def _subscribe_chat_message_created(self, chat_id):
        _uuid = str(uuid.uuid4())
        self.chat_subscriptions[_uuid] = chat_id
        self.ws.send(json.dumps({
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
    
    def _proccess_new_chat_message(self, chat, message):
        events = []
        is_subscribed = self._is_chat_subscribed(chat.id)
        is_new_chat = chat.id not in [chat_.id for chat_ in self.chats]

        if is_new_chat:
            self.chats.append(chat)
        else:
            for old_chat in list(self.chats):
                if old_chat.id == chat.id:
                    self.chats.remove(old_chat)
                    self.chats.append(chat)
                    break

        if not is_subscribed: # если ещё не были подписаны на чат - подписываемся и получаем новое сообщение в этом ивенте
            self._subscribe_chat_message_created(chat.id)
            if is_new_chat:
                events.append(ChatInitializedEvent(chat))
            events.extend(self._parse_message_events(message, chat))
        # иначе, если уже подписаны на чат - сообщение будет получаться из chatMessageCreated
        
        return events
    
    def proccess_ws_message(self, msg):
        try:
            try: msg_data = json.loads(msg)
            except json.JSONDecodeError: return
            
            self.logger.debug(f"WS -> {msg_data}")
            
            if msg_data["type"] == "connection_ack":
                self._subscribe_chat_updated()
                self._subscribe_user_updated()
                
                for chat_ in self.chats:
                    self._subscribe_chat_message_created(chat_.id)
            else:
                payload_data = msg_data.get("payload", {}).get("data", {})
                
                if "userUpdated" in payload_data:
                    unread_chats = payload_data["userUpdated"].get("unreadChatsCounter", 0)
                    if unread_chats > 0:
                        self._possible_new_chat.set()

                if "chatUpdated" in payload_data:
                    _chat = chat(payload_data["chatUpdated"])
                    _message = chat_message(payload_data["chatUpdated"]["lastMessage"])

                    events = self._proccess_new_chat_message(_chat, _message)
                    for event in events:
                        #yield event
                        self.q.put(event)

                if "chatMessageCreated" in payload_data:
                    chat_id = self.chat_subscriptions.get(msg_data["id"])
                    try: _chat = [chat_ for chat_ in self.chats if chat_.id == chat_id][0]
                    except: return
                    _message = chat_message(payload_data["chatMessageCreated"])

                    events = self._parse_message_events(_message, _chat)
                    for event in events:
                        #yield event
                        self.q.put(event)
        except Exception:
            self.logger.debug(f"Ошибка обработки сообщения в WebSocket`е: {traceback.format_exc()}")
        
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

        # try:
        #     ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        #     ssl_context.check_hostname = True
        #     ssl_context.verify_mode = ssl.CERT_NONE
        #     ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        #     ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
        #     ssl_context.load_verify_locations(certifi.where())
        # except:
        #     ssl_context = None

        try: self.chats = self.account.get_chats(count=24).chats # инициализация первых 24 чатов
        except: self.chats = []
        
        for chat_ in self.chats:
            yield ChatInitializedEvent(chat_)

        while True:
            try:
                self.ws = websocket.WebSocket(
                    sslopt={"ca_certs": self.account._tmp_cert_path}
                )
                self.ws.connect(
                    url="wss://ws.playerok.com/graphql",
                    header=[f"{k}: {v}" for k, v in headers.items()],
                    subprotocols=["graphql-transport-ws"]
                )
                self._send_connection_init()          

                while True:
                    msg = self.ws.recv()
                    Thread(target=self.proccess_ws_message, args=(msg,), daemon=True).start()
            except websocket._exceptions.WebSocketException:
                time.sleep(3)
                pass

    def _should_check_review_deal(self, deal_id, delay=30, max_tries=30) -> bool:
        now = time.time()
        info = self.review_deal_times.get(deal_id, {"last": 0, "tries": 0})
        last_time = info["last"]
        tries = info["tries"]
        
        if now - last_time > delay:
            self.review_deal_times[deal_id] = {
                "last": now,
                "tries": tries+1
            }
            return True
        elif tries >= max_tries:
            if deal_id in self.review_check_deals:
                self.review_check_deals.remove(deal_id)
            del self.review_deal_times[deal_id]

        return False
    
    def listen_new_reviews(self):
        while True:
            for deal_id in list(self.review_check_deals):
                try:
                    if not self._should_check_review_deal(deal_id):
                        continue
                    
                    try: deal = self.account.get_deal(deal_id)
                    except: continue
                    
                    if deal.review:
                        if deal_id in self.review_check_deals:
                            self.review_check_deals.remove(deal_id)
                        
                        try: deal.chat = [chat_ for chat_ in self.chats if chat_.id == deal.chat.id][0]
                        except: 
                            try: deal.chat = self.account.get_chat(deal.chat.id)
                            except: pass
                        
                        yield NewReviewEvent(deal, deal.chat)
                except:
                    self.logger.debug(f"Ошибка проверки новых отзывов в сделке {deal_id}: {traceback.format_exc()}")
            time.sleep(1)

    def _wait_for_check_new_chats(self, delay=10):
        sleep_time = delay - (time.time() - self._last_chat_check)
        if sleep_time > 0: time.sleep(sleep_time)
    
    def listen_new_deals(self): # слушает новые сделки в новосозданных чатах
        while True:
            try:
                self._possible_new_chat.wait()
                self._wait_for_check_new_chats()

                self._last_chat_check = time.time()
                self._possible_new_chat.clear()
                
                new_deals = {} # chat: deal_msg
                chats = []
                for _ in range(3):
                    try: chats = self.account.get_chats(count=5, type=ChatTypes.PM).chats
                    except: time.sleep(4)

                    for chat in chats:
                        if chat.last_message.text == "{{ITEM_PAID}}":
                            new_deals[chat] = chat.last_message
                    
                    if new_deals: break
                    else: time.sleep(4)
                
                for chat, msg in new_deals.items():
                    events = self._proccess_new_chat_message(chat, msg)
                    for event in events:
                        yield event
            except websocket._exceptions.WebSocketException:
                pass
            except:
                self.logger.debug(f"Ошибка проверки новых сделок: {traceback.format_exc()}")

    '''def listen_deal_statuses(self): # слушает изменения статусов во всех активных сделках
        while True: # TODO: Доработать, проверить ещё раз на баги 
            for chat_id, deals in list(self.active_deals.items()):
                for _ in range(3):
                    try: 
                        msg_list = self.account.get_chat_messages(chat_id, 24)
                        messages = sorted(
                            msg_list.messages, 
                            key=lambda x: datetime.fromisoformat(x.created_at)
                        )
                        break
                    except: 
                        time.sleep(4)
                
                for deal_id, last_status, status_date in deals:
                    try:
                        status_msgs = [
                            msg for msg in messages 
                            if datetime.fromisoformat(msg.created_at) 
                            >= status_date and msg.deal.status
                        ]

                        for msg in status_msgs:
                            msg_date = datetime.fromisoformat(msg.created_at)
                            if msg.deal.status == last_status and msg_date == status_date:
                                continue
                            
                            try: chat = self.account.get_chat(chat_id)
                            except: chat = None
                            
                            events = self._parse_message_events(msg, chat)
                            for event in events:
                                yield event
                    except:
                        self.logger.debug(f"Ошибка проверки статусов в сделке {deal_id}: {traceback.format_exc()}")
                    time.sleep(8)
            time.sleep(1)'''

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
        if not any((get_new_review_events, get_new_message_events)):
            return
        
        self.q = Queue()

        def run(gen):
            for event in gen:
                self.q.put(event)

        if get_new_message_events:
            Thread(target=run, args=(self.listen_new_messages(),), daemon=True).start()
            Thread(target=run, args=(self.listen_new_deals(),), daemon=True).start()
            #Thread(target=run, args=(self.listen_deal_statuses(),), daemon=True).start()
        
        if get_new_review_events:
            Thread(target=run, args=(self.listen_new_reviews(),), daemon=True).start()

        while True:
            yield self.q.get()