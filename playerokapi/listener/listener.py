import json
import uuid
import time
import traceback
from datetime import datetime, timezone
from logging import getLogger
from typing import Generator
from threading import Thread, Lock, RLock
from queue import Queue
from threading import Event as ThreadingEvent
from collections import deque, OrderedDict

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


logger = getLogger("playerokapi.listener")


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

        self.processed_msgs = deque(maxlen=300)

        self._possible_new_chat = ThreadingEvent()
        self._last_chats_check = 0

        self._state_lock = RLock()
        self._send_lock = Lock()

        self.ws_workers = 12
        self._ws_queue = Queue()
        self._ws_workers_started = False

        self.ws_ping_interval = 30
        self.ws_connect_timeout = 15
        self.catch_up_max_age = 600
        self._started_at = time.time()
        self._ws_last_recv = 0
        self._ws_lost_at = None
        self._ws_alarm = False
        self._ws_gen = 0
        self._clock_offset = 0.0 # серверное время − локальное, по свежим сообщениям из WS
        self._claimed_ids = OrderedDict()

    def _parse_iso(self, iso_dt: str):
        if iso_dt.endswith("Z"):
            iso_dt = iso_dt[:-1] + "+00:00"
        return datetime.fromisoformat(iso_dt)

    def _get_actual_message(
        self, message_id: str, chat_id: str
    ) -> ChatMessage:
        for _ in range(3):
            time.sleep(6)
            
            try: msg_list = self.account.get_chat_messages(chat_id, count=12)
            except: return
            
            try: return [msg for msg in msg_list.messages if msg.id == message_id][0]
            except: pass

    def _get_actual_deal( # получает свежие данные о сделки, ибо в новом ивенте она приходит устаревшая
        self, deal_id: str
    ) -> ItemDeal:
        for _ in range(3):
            try: return self.account.get_deal(deal_id)
            except: pass
            
            time.sleep(3)

    def _set_active_deal(
        self, chat: Chat, deal: ItemDeal, status_date: datetime
    ):
        with self._state_lock:
            if chat.id not in self.active_deals:
                self.active_deals[chat.id] = []

            try: deal_tuple = [tuple for tuple in self.active_deals[chat.id] if deal.id in tuple][0]
            except: deal_tuple = ()

            if not deal_tuple:
                self.active_deals[chat.id].append((deal.id, deal.status, status_date))
            else:
                indx = self.active_deals[chat.id].index(deal_tuple)
                self.active_deals[chat.id][indx] = (deal.id, deal.status, status_date)

    def _is_msg_processed(
        self, message_id: str
    ):
        with self._state_lock:
            return any((
                msg for msg, _ in self.processed_msgs
                if msg.id == message_id
            ))

    def _claim_msg(self, message: ChatMessage, chat_id: str) -> bool:
        if not message:
            return False
        with self._state_lock:
            if message.id in self._claimed_ids or self._is_msg_processed(message.id):
                return False
            # processed_msgs держит только 300 последних — догон за 10 минут может выйти за него
            self._claimed_ids[message.id] = True
            if len(self._claimed_ids) > 3000:
                self._claimed_ids.popitem(last=False)
            self.processed_msgs.append((message, chat_id))
            return True

    def _msg_timestamp(self, message: ChatMessage) -> float:
        try: return self._parse_iso(message.created_at).astimezone(timezone.utc).timestamp()
        except: return 0

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
        
        if not message.text: # фото без подписи (CHAT_STARTED/CHAT_FINISHED тоже без текста, но и без картинок)
            if not message.images:
                return []
            message.text = None # модули отсекают сообщения без текста по `is None`, пустая строка пролезет в их логику
            return [NewMessageEvent(message, chat)]
        
        if message.text == "{{ITEM_PAID}}":
            actual_msg = self._get_actual_message(message.id, chat.id) or message
            actual_deal = self._get_actual_deal(actual_msg.deal.id) or message.deal
            
            if actual_msg and actual_deal:
                deal_id = actual_deal.id
                #status_date = self._parse_iso(actual_msg.created_at)
                #self._set_active_deal(chat, actual_deal, status_date)
                with self._state_lock:
                    if deal_id not in self.review_check_deals:
                        self.review_check_deals.append(deal_id)
                    if deal_id not in self.processed_deals:
                        self.processed_deals.append(deal_id)
                    else:
                        return []
                return [
                    NewDealEvent(actual_deal, chat),
                    ItemPaidEvent(actual_deal, chat)
                ]
        
        elif message.text == "{{ITEM_SENT}}":
            actual_msg = self._get_actual_message(message.id, chat.id) or message
            actual_deal = self._get_actual_deal(actual_msg.deal.id) or message.deal
            
            if actual_msg and actual_deal:
                #status_date = self._parse_iso(actual_msg.created_at)
                #self._set_active_deal(chat, actual_deal, status_date)
                return [
                    ItemSentEvent(actual_deal, chat),
                    DealStatusChangedEvent(actual_deal, chat)
                ]
        
        elif message.text.startswith("{{DEAL_CONFIRMED") and message.text.endswith("}}"): # DEAL_CONFIRMED, DEAL_CONFIRMED_AUTOMATICALLY
            actual_msg = self._get_actual_message(message.id, chat.id) or message
            actual_deal = self._get_actual_deal(actual_msg.deal.id) or message.deal
            
            if actual_msg and actual_deal:
                #status_date = self._parse_iso(actual_msg.created_at)
                #self._set_active_deal(chat, actual_deal, status_date)
                return [
                    DealConfirmedEvent(actual_deal, chat),
                    DealStatusChangedEvent(actual_deal, chat),
                ]
        
        elif message.text == "{{DEAL_ROLLED_BACK}}":
            actual_msg = self._get_actual_message(message.id, chat.id) or message
            actual_deal = self._get_actual_deal(actual_msg.deal.id) or message.deal
            
            if actual_msg and actual_deal:
                #status_date = self._parse_iso(actual_msg.created_at)
                #self._set_active_deal(chat, actual_deal, status_date)
                return [
                    DealRolledBackEvent(actual_deal, chat),
                    DealStatusChangedEvent(actual_deal, chat),
                ]
        
        elif message.text == "{{DEAL_HAS_PROBLEM}}":
            actual_msg = self._get_actual_message(message.id, chat.id) or message
            actual_deal = self._get_actual_deal(actual_msg.deal.id) or message.deal
            
            if actual_msg and actual_deal:
                #status_date = self._parse_iso(actual_msg.created_at)
                #self._set_active_deal(chat, actual_deal, status_date)
                return [
                    DealHasProblemEvent(actual_deal, chat),
                    DealStatusChangedEvent(actual_deal, chat),
                ]
        
        elif message.text == "{{DEAL_PROBLEM_RESOLVED}}":
            actual_msg = self._get_actual_message(message.id, chat.id) or message
            actual_deal = self._get_actual_deal(actual_msg.deal.id) or message.deal
            
            if actual_msg and actual_deal:
                #status_date = self._parse_iso(actual_msg.created_at)
                #self._set_active_deal(chat, actual_deal, status_date)
                return [
                    DealProblemResolvedEvent(actual_deal, chat),
                    DealStatusChangedEvent(actual_deal, chat),
                ]
        
        return [NewMessageEvent(message, chat)]
    
    def _send_connection_init(self):
        with self._send_lock:
            self.ws.send(json.dumps({
                "type": "connection_init",
                "payload": {
                    "x-gql-op": "ws-subscription",
                    "x-gql-path": "/chats/[id]",
                    "x-timezone-offset": -180
                }
            }))

    def _send_ping(self):
        with self._send_lock:
            self.ws.send(json.dumps({"type": "ping"}))

    def _send_pong(self):
        with self._send_lock:
            self.ws.send(json.dumps({"type": "pong"}))

    def _subscribe_chat_updated(self):
        with self._send_lock:
            self.ws.send(json.dumps({
                "id": str(uuid.uuid4()),
                "type": "subscribe",
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
            }))

    def _subscribe_chat_marked_as_read(self):
        with self._send_lock:
            self.ws.send(json.dumps({
                "id": str(uuid.uuid4()),
                "type": "subscribe",
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
                }
            }))

    def _subscribe_user_updated(self):
        with self._send_lock:
            self.ws.send(json.dumps({
                "id": str(uuid.uuid4()),
                "type": "subscribe",
                "payload": {
                    "extensions": {},
                    "operationName": "userUpdated",
                    "query": QUERIES.get("userUpdated"),
                    "variables": {
                        "userId": self.account.id
                    }
                }
            }))

    def _subscribe_chat_message_created(self, chat_id):
        _uuid = str(uuid.uuid4())
        with self._state_lock:
            self.chat_subscriptions[_uuid] = chat_id
        try:
            with self._send_lock:
                self.ws.send(json.dumps({
                    "id": _uuid,
                    "type": "subscribe",
                    "payload": {
                        "extensions": {},
                        "operationName": "chatMessageCreated",
                        "query": QUERIES.get("chatMessageCreated"),
                        "variables": {
                            "filter": {
                                "chatId": chat_id
                            }
                        }
                    }
                }))
        except Exception:
            # иначе чат числится подписанным и больше никогда не переподпишется
            with self._state_lock:
                self.chat_subscriptions.pop(_uuid, None)
            raise

    def _is_chat_subscribed(self, chat_id):
        with self._state_lock:
            for _, sub_chat_id in self.chat_subscriptions.items():
                if chat_id == sub_chat_id:
                    return True
            return False
    
    def _proccess_new_chat_message(self, chat, message):
        events = []
        with self._state_lock:
            is_new_chat = chat.id not in [chat_.id for chat_ in self.chats]

            if is_new_chat:
                self.chats.append(chat)
            else:
                for old_chat in list(self.chats):
                    if old_chat.id == chat.id:
                        self.chats.remove(old_chat)
                        self.chats.append(chat)
                        break

            if not self._is_msg_processed(message.id):
                self.processed_msgs.append((message, chat.id))

        events.extend(self._parse_message_events(message, chat))
        return events

    def _process_chats_last_messages(self, chats):
        now = datetime.now(timezone.utc)

        with self._state_lock:
            for chat in chats:
                msg = chat.last_message
                if (
                    msg
                    and (now - self._parse_iso(msg.created_at).astimezone(timezone.utc)).total_seconds() > 90
                    and not self._is_msg_processed(msg.id)
                ):
                    self.processed_msgs.append((msg, chat.id))

    def _catch_up_messages(self, lost_at: float) -> bool:
        # подписки не присылают то, что пришло, пока WS был отключён — добираем через историю чатов.
        # created_at серверный, поэтому окно сдвигаем на расхождение часов ПК с сервером
        offset = self._clock_offset
        since = max(lost_at - 30, self._started_at) + offset
        oldest = time.time() + offset - self.catch_up_max_age
        if since < oldest:
            logger.warning(
                f"Связи с Playerok не было дольше {self.catch_up_max_age // 60} минут — "
                f"сообщения из чатов раньше этого не восстановлены"
            )
            since = oldest

        chats = None
        for _ in range(3):
            try:
                chats = self.account.get_chats(count=24).chats
                break
            except Exception:
                logger.debug(f"Не удалось получить чаты для догона сообщений: {traceback.format_exc()}")
                time.sleep(2)
        if chats is None:
            return False

        for chat_ in chats:
            if not chat_.last_message or self._msg_timestamp(chat_.last_message) < since:
                continue

            if not self._is_chat_subscribed(chat_.id):
                self._subscribe_chat_message_created(chat_.id)

            try: messages = self.account.get_chat_messages(chat_.id, count=24).messages
            except Exception: messages = [chat_.last_message]

            for message in sorted(messages, key=self._msg_timestamp):
                if self._msg_timestamp(message) < since:
                    continue
                if not self._claim_msg(message, chat_.id):
                    continue
                if (
                    message.user and message.user.id == self.account.id
                    and not (message.text or "").startswith("{{")
                ):
                    continue

                logger.debug(f"Догнал пропущенное сообщение {message.id} в чате {chat_.id}")
                for event in self._proccess_new_chat_message(chat_, message):
                    self.q.put(event)

            time.sleep(0.5)
        return True

    def _on_connection_ack(self):
        with self._state_lock:
            # подписки прошлого соединения мертвы — иначе _is_chat_subscribed врёт и чат не переподпишется
            self.chat_subscriptions.clear()
            chats_snapshot = list(self.chats)
            lost_at, self._ws_lost_at = self._ws_lost_at, None

        caught_up = False
        try:
            self._subscribe_chat_updated()
            self._subscribe_user_updated()
            for chat_ in chats_snapshot:
                self._subscribe_chat_message_created(chat_.id)
            caught_up = not lost_at or self._catch_up_messages(lost_at)
        finally:
            if lost_at and not caught_up:
                # не догнали — повторим на следующем подключении с того же места
                with self._state_lock:
                    self._ws_lost_at = min(lost_at, self._ws_lost_at or lost_at)

    def proccess_ws_message(self, msg, gen: int | None = None):
        try:
            try: msg_data = json.loads(msg)
            except json.JSONDecodeError: return

            if msg_data.get("type") == "ping":
                self._send_pong()
                return
            if msg_data.get("type") == "pong":
                return

            logger.debug(f"WS -> {msg_data}")

            if msg_data["type"] == "connection_ack":
                if gen is not None and gen != self._ws_gen:
                    return # ack прошлого соединения, пролежавший в очереди
                self._on_connection_ack()
            else:
                payload_data = (msg_data.get("payload") or {}).get("data") or {}
                
                if "userUpdated" in payload_data:
                    unread_chats = payload_data["userUpdated"].get("unreadChatsCounter", 0)
                    if unread_chats > 0:
                        self._possible_new_chat.set()

                if "chatUpdated" in payload_data:
                    _chat = chat(payload_data["chatUpdated"])
                    _message = chat_message(payload_data["chatUpdated"]["lastMessage"])

                    if not self._is_chat_subscribed(_chat.id):
                        self._subscribe_chat_message_created(_chat.id)
                        
                        events = [ChatInitializedEvent(_chat)]
                        events.extend(self._proccess_new_chat_message(_chat, _message))
                        for event in events:
                            # yield event
                            self.q.put(event)

                if "chatMessageCreated" in payload_data:
                    chat_id = self.chat_subscriptions.get(msg_data["id"])
                    with self._state_lock:
                        _chat = next((chat_ for chat_ in self.chats if chat_.id == chat_id), None)
                    if _chat is None:
                        logger.debug(f"Чат {chat_id} ещё не в self.chats — пропуск chatMessageCreated")
                        return
                    _message = chat_message(payload_data["chatMessageCreated"])
                    # одно сообщение могут прислать дважды (двойная подписка) или его уже выпустил догон
                    if not self._claim_msg(_message, _chat.id):
                        return
                    ts = self._msg_timestamp(_message)
                    if ts:
                        self._clock_offset = ts - time.time()

                    events = self._proccess_new_chat_message(_chat, _message)
                    for event in events:
                        # yield event
                        self.q.put(event)
        except Exception:
            logger.debug(f"Ошибка обработки сообщения в WebSocket`е: {traceback.format_exc()}")

    def _ws_worker(self):
        while True:
            gen, msg = self._ws_queue.get()
            try:
                self.proccess_ws_message(msg, gen)
            except Exception:
                logger.debug(f"Ошибка обработки сообщения в WebSocket`е: {traceback.format_exc()}")

    def _start_ws_workers(self):
        with self._state_lock:
            if self._ws_workers_started:
                return
            self._ws_workers_started = True
        for _ in range(self.ws_workers):
            Thread(target=self._ws_worker, daemon=True).start()

    def listen_new_messages(self):
        headers = {
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "ru,en;q=0.9",
            "cache-control": "no-cache",
            "connection": "Upgrade",
            "origin": "https://playerok.com",
            "pragma": "no-cache",
            "sec-websocket-extensions": "permessage-deflate; client_max_window_bits",
            "cookie": "; ".join([f"{k}={v}" for k, v in self.account.cookies.items()]),
            "user-agent": self.account.user_agent
        }

        proxy_host, proxy_port, proxy_auth = None, None, None
        
        if self.account.proxy:
            if "@" in self.account.proxy:
                proxy_host, proxy_port = self.account.proxy.split("@")[1].split(":")
                proxy_username, proxy_password = self.account.proxy.split("@")[0].split(":")
                proxy_auth = (proxy_username, proxy_password)
            else:
                proxy_host, proxy_port = self.account.proxy.split(":")

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

        self._started_at = time.time()
        try: self._process_chats_last_messages(self.chats)
        except Exception: logger.debug(f"Ошибка разбора последних сообщений чатов: {traceback.format_exc()}")

        with self._state_lock:
            chats_snapshot = list(self.chats)
        for chat_ in chats_snapshot:
            yield ChatInitializedEvent(chat_)

        self._start_ws_workers()

        fails = 0
        while True:
            connected_at = time.time()
            self._ws_gen += 1
            try:
                self.ws = websocket.WebSocket(
                    sslopt={"ca_certs": self.account._tmp_cert_path}
                )
                self.ws.connect(
                    url="wss://ws.playerok.com/graphql",
                    header=[f"{k}: {v}" for k, v in headers.items()],
                    subprotocols=["graphql-transport-ws"],
                    http_proxy_host=proxy_host,
                    http_proxy_port=proxy_port,
                    http_proxy_auth=proxy_auth,
                    timeout=self.ws_connect_timeout
                )
                self.ws.settimeout(self.ws_ping_interval)
                self._send_connection_init()
                self._recv_ws_messages()
            except Exception:
                # ConnectionResetError (WinError 10054), SSLError, OSError — не WebSocketException,
                # раньше они молча убивали поток и бот переставал видеть сообщения
                worked = self._ws_last_recv >= connected_at and time.time() - connected_at >= 60 # рвётся сразу — не рабочее
                fails = 1 if worked else fails + 1
                with self._state_lock:
                    if self._ws_lost_at is None:
                        # не подключились с самого старта — догоняем с момента запуска
                        self._ws_lost_at = self._ws_last_recv or self._started_at

                try: self.ws.shutdown()
                except Exception: pass

                if fails <= 3:
                    logger.debug(f"Соединение с WebSocket потеряно (попытка {fails}): {traceback.format_exc()}")
                else:
                    logger.debug(f"Соединение с WebSocket потеряно (попытка {fails})")
                if fails == 3:
                    self._ws_alarm = True
                    logger.warning("Нет соединения с Playerok, новые сообщения не приходят. Переподключаюсь...")
                time.sleep(min(3 * fails, 30))

    def _recv_ws_messages(self):
        awaiting_pong = False
        while True:
            try:
                msg = self.ws.recv()
            except websocket._exceptions.WebSocketTimeoutException:
                # долго тихо — проверяем, живо ли соединение. не ответил на ping — переподключаемся
                if awaiting_pong:
                    raise
                self._send_ping()
                awaiting_pong = True
                continue

            awaiting_pong = False
            self._ws_last_recv = time.time()
            if self._ws_alarm:
                self._ws_alarm = False
                logger.info("Соединение с Playerok восстановлено, сообщения снова приходят")
            self._ws_queue.put((self._ws_gen, msg))

    def _should_check_review_deal(self, deal_id, delay=30, max_tries=30) -> bool:
        with self._state_lock:
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
                        with self._state_lock:
                            if deal_id in self.review_check_deals:
                                self.review_check_deals.remove(deal_id)

                        try:
                            with self._state_lock:
                                deal.chat = [chat_ for chat_ in self.chats if chat_.id == deal.chat.id][0]
                        except:
                            try: deal.chat = self.account.get_chat(deal.chat.id)
                            except: pass
                        
                        yield NewReviewEvent(deal, deal.chat)
                except:
                    logger.debug(f"Ошибка проверки новых отзывов в сделке {deal_id}: {traceback.format_exc()}")
            time.sleep(1)

    def _wait_for_check_new_chats(self, delay=10):
        sleep_time = delay - (time.time() - self._last_chats_check)
        if sleep_time > 0: 
            time.sleep(sleep_time)

    def listen_new_deals(self):
        while True:
            try:
                by_event = self._possible_new_chat.wait(timeout=15)
                if by_event:
                    self._possible_new_chat.clear()
                    self._wait_for_check_new_chats()

                possible_chats = []
                now = datetime.now(timezone.utc)

                for _ in range(3):
                    try:
                        if by_event:
                            time.sleep(8) # плеерок может не сразу отобразить актуальные чаты
                        
                        chats = self.account.get_chats(count=15, type=ChatTypes.PM).chats
                        for chat in chats:
                            last_msg = chat.last_message
                            if not last_msg:
                                continue
                            is_msg_processed = self._is_msg_processed(last_msg.id)
                            with self._state_lock:
                                is_chat_processed = any(_chat.id == chat.id for _chat in self.chats)

                            if (
                                not is_chat_processed
                                or not is_msg_processed or (
                                    is_msg_processed
                                    and (now - self._parse_iso(last_msg.created_at).astimezone(timezone.utc)).total_seconds() <= 90
                                )
                            ):
                                if chat.id not in [c.id for c in possible_chats]:
                                    possible_chats.append(chat)

                        if possible_chats:
                            break # если найдены чаты с возможными новыми сделками - останавливаем цикл

                        if not by_event:
                            time.sleep(8)
                    except:
                        pass

                for chat in possible_chats:
                    last_msg = chat.last_message
                    
                    # Новый чат — смотрим last_message сначала (быстрый путь)
                    if (
                        last_msg and last_msg.text == "{{ITEM_PAID}}"
                        and (now - self._parse_iso(last_msg.created_at).astimezone(timezone.utc)).total_seconds() <= 90
                    ):
                        events = self._proccess_new_chat_message(chat, last_msg)
                        for event in events:
                            yield event
                        continue

                    # медленный путь: last_message перебит новым сообщением от покупателя.
                    # запрашиваем историю и ищем {{ITEM_PAID}} среди первых сообщений.
                    try:
                        time.sleep(1)
                        messages = self.account.get_chat_messages(chat.id, count=12).messages
                        new_paid_msg = next(
                            (
                            msg for msg in messages
                            if msg.text == "{{ITEM_PAID}}"
                            and (now - self._parse_iso(msg.created_at).astimezone(timezone.utc)).total_seconds() <= 90 
                            # ^ проверка на то, что эта сделка была совершена недавно
                            ),
                            None
                        )
                        
                        if new_paid_msg:
                            events = self._proccess_new_chat_message(chat, new_paid_msg)
                            for event in events:
                                yield event
                    except:
                        logger.debug(f"Ошибка получения истории сообщений нового чата {chat.id}: {traceback.format_exc()}")
            except websocket._exceptions.WebSocketException:
                pass
            except:
                logger.debug(f"Ошибка проверки новых сделок: {traceback.format_exc()}")
            
            self._last_chats_check = time.time()

    def listen_deal_statuses(self): # слушает изменения статусов во всех активных сделках
        while True: # TODO: Доработать, проверить ещё раз на баги 
            for chat_id, deals in list(self.active_deals.items()):
                for _ in range(3):
                    try: 
                        msg_list = self.account.get_chat_messages(chat_id, 24)
                        messages = sorted(
                            msg_list.messages, 
                            key=lambda x: self._parse_iso(x.created_at)
                        )
                        break
                    except: 
                        time.sleep(6)
                
                for deal_id, last_status, status_date in deals:
                    try:
                        status_msgs = [
                            msg for msg in messages 
                            if self._parse_iso(msg.created_at) 
                            >= status_date and msg.deal.status
                        ]

                        for msg in status_msgs:
                            msg_date = self._parse_iso(msg.created_at)
                            if msg.deal.status == last_status and msg_date == status_date:
                                continue
                            
                            try: chat = self.account.get_chat(chat_id)
                            except: continue
                            
                            events = self._parse_message_events(msg, chat)
                            for event in events:
                                yield event

                            self._set_active_deal(chat, msg.deal, msg_date)
                    except:
                        logger.debug(f"Ошибка проверки статусов в сделке {deal_id}: {traceback.format_exc()}")
                    time.sleep(8)
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
        if not any((get_new_review_events, get_new_message_events)):
            return
        
        self.q = Queue()

        def run(listen_func):
            while True:
                try:
                    for event in listen_func():
                        self.q.put(event)
                except Exception:
                    logger.error(f"Слушатель {listen_func.__name__} упал, перезапускаю: {traceback.format_exc()}")
                time.sleep(10)

        if get_new_message_events:
            Thread(target=run, args=(self.listen_new_messages,), daemon=True).start()
            Thread(target=run, args=(self.listen_new_deals,), daemon=True).start()
            #Thread(target=run, args=(self.listen_deal_statuses,), daemon=True).start()
        
        if get_new_review_events:
            Thread(target=run, args=(self.listen_new_reviews,), daemon=True).start()

        while True:
            yield self.q.get()