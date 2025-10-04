import asyncio
import time
from datetime import datetime, timedelta
import time
import traceback
from threading import Thread
from colorama import Fore, Style
from aiogram.types import InlineKeyboardMarkup

import settings
from settings import Settings as sett
from logging import getLogger
from data import Data as data
from .stats import get_stats, set_stats

from playerokapi.account import Account
from playerokapi import exceptions as plapi_exceptions
from playerokapi.enums import *
from playerokapi.listener.events import *
from playerokapi.listener.listener import EventListener
from playerokapi.types import Chat, Item

from __init__ import VERSION, ACCENT_COLOR
from core.console import set_title, restart
from core.handlers_manager import HandlersManager

from . import set_playerok_bot
from tgbot import get_telegram_bot, get_telegram_bot_loop
from tgbot.templates import log_text, log_new_mess_kb, log_new_deal_kb

PREFIX = F"{Fore.CYAN}[PL]{Fore.WHITE}"



class PlayerokBot:
    """
    Класс, запускающий и инициализирующий Playerok бота.
    """

    def __init__(self):
        self.config = sett.get("config")
        self.messages = sett.get("messages")
        self.custom_commands = sett.get("custom_commands")
        self.auto_deliveries = sett.get("auto_deliveries")
        self.logger = getLogger(f"universal.playerok")

        try:
            self.playerok_account = Account(token=self.config["playerok"]["api"]["token"],
                                            user_agent=self.config["playerok"]["api"]["user_agent"],
                                            requests_timeout=self.config["playerok"]["api"]["requests_timeout"],
                                            proxy=self.config["playerok"]["api"]["proxy"] or None).get()
            """ Класс, содержащий данные и методы аккаунта Playerok """
        except plapi_exceptions.UnauthorizedError as e:
            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Не удалось подключиться к вашему Playerok аккаунту. Ошибка: {Fore.WHITE}{e}")
            print(f"{Fore.WHITE}🔑  Указать новый {Fore.LIGHTCYAN_EX}token{Fore.WHITE}? +/-")
            a = input(f"{Fore.WHITE}→ {Fore.LIGHTWHITE_EX}")
            if a == "+":
                param = {"playerok": {"api": {"token": settings.DATA["config"]["params"]["playerok"]["api"]["token"]}}}
                sett.configure("config", ACCENT_COLOR, params=param)
                restart()
            else:
                self.logger.info(f"{PREFIX} Вы отказались от настройки конфига. Перезагрузим бота и попробуем снова подключиться к вашему аккаунту...")
                restart()

        self.initialized_users: list = data.get("initialized_users")
        """ Инициализированные в диалоге пользователи. """
        self.stats = get_stats()
        """ Словарь статистика бота с момента запуска. """

        self.__saved_chats: dict[str, Chat] = {}
        """ 
        Словарь последних запомненных чатов.\n
        В формате: {`chat_id` _or_ `username`: `chat_obj`, ...}
        """

        set_playerok_bot(self)

    def get_chat_by_id(self, chat_id: str) -> Chat:
        """ 
        Получает чат с пользователем из запомненных чатов по его ID.
        Запоминает и получает чат, если он не запомнен.
        """
        if chat_id in self.__saved_chats:
            return self.__saved_chats[chat_id]
        self.__saved_chats[chat_id] = self.playerok_account.get_chat(chat_id)
        return self.get_chat_by_id(chat_id)

    def get_chat_by_username(self, username: str) -> Chat:
        """ 
        Получает чат с пользователем из запомненных чатов по никнейму собеседника.
        Запоминает и получает чат, если он не запомнен.
        """
        if username in self.__saved_chats:
            return self.__saved_chats[username]
        self.__saved_chats[username] = self.playerok_account.get_chat_by_username(username)
        return self.get_chat_by_username(username)

    def get_my_items(self, statuses: list[ItemStatuses] | None = None) -> list[types.ItemProfile]:
        """
        Получает все предметы аккаунта.
        """
        user = self.playerok_account.get_user(self.playerok_account.id)
        my_items: list[types.ItemProfile] = []
        next_cursor = None
        stop = False
        while not stop:
            _items = user.get_items(statuses=statuses, after_cursor=next_cursor)
            for _item in _items.items:
                if _item.id not in [item.id for item in my_items]:
                    my_items.append(_item)
            if not _items.page_info.has_next_page:
                break
            next_cursor = _items.page_info.end_cursor
            time.sleep(0.1)
        return my_items
    

    def msg(self, message_name: str, exclude_watermark: bool = False, **kwargs) -> str:
        """ 
        Получает отформатированное сообщение из словаря сообщений.

        :param message_name: Наименование сообщения в словаре сообщений (ID).
        :type message_name: str

        :param exclude_watermark: Пропустить и не использовать водяной знак.
        :type exclude_watermark: bool
        """

        class SafeDict(dict):
            def __missing__(self, key):
                return "{" + key + "}"
        
        message_lines: list[str] = self.messages[message_name]
        if message_lines:
            try:
                formatted_lines = [line.format_map(SafeDict(**kwargs)) for line in message_lines]
                msg = "\n".join(formatted_lines)
                if not exclude_watermark and self.config["playerok"]["bot"]["messages_watermark_enabled"]:
                    msg += f'\n{self.config["playerok"]["bot"]["messages_watermark"]}'
                return msg
            except:
                pass
        return "Не удалось получить сообщение"
    
    def send_message(self, chat_id: str, text: str | None = None, photo_file_path: str | None = None,
                     mark_chat_as_read: bool = None, max_attempts: int = 3) -> types.ChatMessage:
        """
        Кастомный метод отправки сообщения в чат Playerok.
        Пытается отправить за 3 попытки, если не удалось - выдаёт ошибку в консоль.\n
        Можно отправить текстовое сообщение `text` или фотографию `photo_file_path`.

        :param chat_id: ID чата, в который нужно отправить сообщение.
        :type chat_id: `str`

        :param text: Текст сообщения, _опционально_.
        :type text: `str` or `None`

        :param photo_file_path: Путь к файлу фотографии, _опционально_.
        :type photo_file_path: `str` or `None`

        :param mark_chat_as_read: Пометить чат, как прочитанный перед отправкой, _опционально_.
        :type mark_chat_as_read: `bool`

        :return: Объект отправленного сообщения.
        :rtype: `PlayerokAPI.types.ChatMessage`
        """
        for _ in range(max_attempts):
            try:
                mark_chat_as_read = (self.config["playerok"]["bot"]["read_chat_before_sending_message_enabled"] or False) if mark_chat_as_read is None else mark_chat_as_read
                mess = self.playerok_account.send_message(chat_id, text, photo_file_path, mark_chat_as_read)
                return mess
            except plapi_exceptions.RequestFailedError:
                continue
            except Exception as e:
                text = text.replace('\n', '').strip()
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Ошибка при отправке сообщения {Fore.LIGHTWHITE_EX}«{text}» {Fore.LIGHTRED_EX}в чат {Fore.LIGHTWHITE_EX}{chat_id} {Fore.LIGHTRED_EX}: {Fore.WHITE}{e}")
                return
        text = text.replace('\n', '').strip()
        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Не удалось отправить сообщение {Fore.LIGHTWHITE_EX}«{text}» {Fore.LIGHTRED_EX}в чат {Fore.LIGHTWHITE_EX}{chat_id}")

    def log_to_tg(self, text: str, kb: InlineKeyboardMarkup | None = None):
        """
        Логгирует ивент в Telegram бота.

        :param text: Текст лога.
        :type text: str
        """
        asyncio.run_coroutine_threadsafe(get_telegram_bot().log_event(text, kb), get_telegram_bot_loop())


    async def restore_last_sold_item(self, item: Item):
        """ 
        Восстанавливает последний проданный предмет. 
        
        :param item: Объект предмета, который нужно восстановить.
        :type item: `playerokapi.types.Item`
        """
        try:
            profile = self.playerok_account.get_user(id=self.playerok_account.id)
            items = profile.get_items(count=24, statuses=[ItemStatuses.SOLD]).items
            _item = [profile_item for profile_item in items if profile_item.name == item.name]
            if len(_item) <= 0: return
            try: item: types.MyItem = self.playerok_account.get_item(_item[0].id)
            except: item = _item[0]

            priority_statuses = self.playerok_account.get_item_priority_statuses(item.id, item.price)
            priority_status = None
            for status in priority_statuses:
                if isinstance(item, types.MyItem) and item.priority:
                    if status.type.name == item.priority.name:
                        priority_status = status
                elif status.type is PriorityTypes.DEFAULT:
                    priority_status = status
                if priority_status: break

            new_item = self.playerok_account.publish_item(item.id, priority_status.id)
            if new_item.status is ItemStatuses.PENDING_APPROVAL or new_item.status is ItemStatuses.APPROVED:
                self.logger.info(f"{PREFIX} {Fore.LIGHTWHITE_EX}«{item.name}» {Fore.WHITE}— товар восстановлен ♻️")
            else:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Не удалось восстановить предмет «{new_item.name}». Его статус: {Fore.WHITE}{new_item.status.name}")
        except Exception as e:
            self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При восстановлении предмета «{item.name}» произошла ошибка: {Fore.WHITE}{e}")

    async def run_bot(self):
        self.logger.info(f"{PREFIX} Playerok бот запущен и активен на аккаунте ↓")
        self.logger.info(f"{PREFIX} {Fore.LIGHTWHITE_EX}┏ {ACCENT_COLOR}🆔 ID: {Fore.LIGHTWHITE_EX}{self.playerok_account.profile.id}")
        self.logger.info(f"{PREFIX} {Fore.LIGHTWHITE_EX}┣ {ACCENT_COLOR}👤 Никнейм: {Fore.LIGHTWHITE_EX}{self.playerok_account.username}")
        self.logger.info(f"{PREFIX} {Fore.LIGHTWHITE_EX}┣ {ACCENT_COLOR}💰 Баланс: {Fore.LIGHTWHITE_EX}{self.playerok_account.profile.balance.available}₽" + (f" {Fore.WHITE}(🔒 {self.playerok_account.profile.balance.pending_income}₽)" if self.playerok_account.profile.balance.pending_income else ""))
        self.logger.info(f"{PREFIX} {Fore.LIGHTWHITE_EX}┗ {ACCENT_COLOR}⭐ Рейтинг: {Fore.LIGHTWHITE_EX}{self.playerok_account.profile.rating}")
        if self.config["playerok"]["api"]["proxy"]:
            ip_port = self.config["playerok"]["api"]["proxy"].split("@")[1] if "@" in self.config["playerok"]["api"]["proxy"] else self.config["playerok"]["api"]["proxy"]
            self.logger.info(f"{PREFIX} Playerok бот подключен к прокси {Fore.LIGHTWHITE_EX}{ip_port}")

        def handler_on_playerok_bot_init(plbot: PlayerokBot):
            """ Начальный хендлер ON_INIT. """
            
            self.stats.bot_launch_time = datetime.now()
            set_stats(self.stats)

            def endless_loop(cycle_delay=5):
                while True:
                    try:
                        set_playerok_bot(plbot)
                        balance = self.playerok_account.profile.balance.value if self.playerok_account.profile.balance is not None else "?"
                        set_title(f"Playerok Universal v{VERSION} | {self.playerok_account.username}: {balance}₽")
                        
                        if data.get("initialized_users") != self.initialized_users: data.set("initialized_users", self.initialized_users)
                        if sett.get("config") != self.config: self.config = sett.get("config")
                        if sett.get("messages") != self.messages: self.messages = sett.get("messages")
                        if sett.get("custom_commands") != self.custom_commands: self.custom_commands = sett.get("custom_commands")
                        if sett.get("auto_deliveries") != self.auto_deliveries: self.auto_deliveries = sett.get("auto_deliveries")
                    except Exception:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}В бесконечном цикле произошла ошибка: {Fore.WHITE}")
                        traceback.print_exc()
                    time.sleep(cycle_delay)

            Thread(target=endless_loop, daemon=True).start()

        bot_event_handlers = HandlersManager.get_bot_event_handlers()
        bot_event_handlers["ON_PLAYEROK_BOT_INIT"].insert(0, handler_on_playerok_bot_init)
        HandlersManager.set_bot_event_handlers(bot_event_handlers)

        async def handler_new_message(plbot: PlayerokBot, event: NewMessageEvent):
            try:
                this_chat = event.chat
                if self.config["playerok"]["bot"]["tg_logging_enabled"] and (self.config["playerok"]["bot"]["tg_logging_events"]["new_user_message"] or self.config["playerok"]["bot"]["tg_logging_events"]["new_system_message"]):
                    if event.message.user.username != self.playerok_account.username:
                        do = False
                        if self.config["playerok"]["bot"]["tg_logging_events"]["new_user_message"] and event.message.user.username not in ["Playerok.com", "Поддержка"]: do = True 
                        if self.config["playerok"]["bot"]["tg_logging_events"]["new_system_message"] and event.message.user.username in ["Playerok.com", "Поддержка"]: do = True 
                        if do:
                            text = f"<b>{event.message.user.username}:</b> {event.message.text or ''}"
                            if event.message.file:
                                text += f' <b><a href="{event.message.file.url}">{event.message.file.filename}</a></b>'
                            self.log_to_tg(text=log_text(f'💬 Новое сообщение в <a href="https://playerok.com/chats/{event.chat.id}">чате</a>', text.strip()),
                                            kb=log_new_mess_kb(event.message.user.username))

                if self.config["playerok"]["bot"]["first_message_enabled"]:
                    if event.message.user is not None:
                        if event.message.user.id != self.playerok_account.id and event.message.user.id not in self.initialized_users and event.chat.id not in [self.playerok_account.system_chat_id, self.playerok_account.support_chat_id]:
                            try:
                                self.send_message(this_chat.id, 
                                                   self.msg("user_not_initialized", username=event.message.user.username))
                                self.initialized_users.append(event.message.user.id)
                            except Exception as e:
                                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При отправке приветственного сообщения для {event.message.user.username} произошла ошибка: {Fore.WHITE}{e}")

                if event.message.user is not None:
                    if event.message.user.id != self.playerok_account.id:
                        if self.config["playerok"]["bot"]["custom_commands_enabled"]:
                            if event.message.text in self.custom_commands.keys():
                                try:
                                    msg = "\n".join(self.custom_commands[event.message.text]) + (f'\n{self.config["playerok"]["bot"]["messages_watermark"]}' if self.config["playerok"]["bot"]["messages_watermark_enabled"] else "")
                                    self.send_message(this_chat.id, msg)
                                except Exception as e:
                                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При вводе пользовательской команды \"{event.message.text}\" у {event.message.user.username} произошла ошибка: {Fore.WHITE}{e}")
                                    self.send_message(this_chat.id, 
                                                       self.msg("command_error"))
                        if str(event.message.text).lower() == "!команды" or str(event.message.text).lower() == "!commands":
                            try:
                                self.send_message(this_chat.id, 
                                                   self.msg("buyer_command_commands"))
                            except Exception as e:
                                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При вводе команды \"!команды\" у {event.message.user.username} произошла ошибка: {Fore.WHITE}{e}")
                                self.send_message(this_chat.id, 
                                                   self.msg("command_error"))
                        if str(event.message.text).lower() == "!продавец" or str(event.message.text).lower() == "!seller":
                            try:
                                asyncio.run_coroutine_threadsafe(get_telegram_bot().call_seller(event.message.user.username, this_chat.id), get_telegram_bot_loop())
                                self.send_message(this_chat.id, 
                                                   self.msg("buyer_command_seller"))
                            except Exception as e:
                                self.logger.log(f"{PREFIX} {Fore.LIGHTRED_EX}При вводе команды \"!продавец\" у {event.message.user.username} произошла ошибка: {Fore.WHITE}{e}")
                                self.send_message(this_chat.id, 
                                                   self.msg("command_error"))
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def handler_new_deal(plbot: PlayerokBot, event: NewDealEvent):
            try:
                this_chat = event.chat
                self.logger.info(f"{PREFIX} {ACCENT_COLOR}📋  Новая сделка: {Fore.LIGHTWHITE_EX}{event.deal.user.username}{Fore.WHITE} оплатил предмет {Fore.LIGHTWHITE_EX}«{event.deal.item.name}»{Fore.WHITE} на сумму {Fore.LIGHTWHITE_EX}{event.deal.item.price or '?'}₽")
                if self.config["playerok"]["bot"]["tg_logging_enabled"] and self.config["playerok"]["bot"]["tg_logging_events"]["new_deal"]:
                    self.log_to_tg(text=log_text(f'📋 Новая <a href="https://playerok.com/deal/{event.deal.id}">сделка</a>', f"<b>Покупатель:</b> {event.deal.user.username}\n<b>Предмет:</b> {event.deal.item.name}\n<b>Сумма:</b> {event.deal.item.price or '?'}₽"),
                                    kb=log_new_deal_kb(event.deal.user.username, event.deal.id))

                if self.config["playerok"]["bot"]["auto_deliveries_enabled"]:
                    for auto_delivery in self.auto_deliveries:
                        for phrase in auto_delivery["keyphrases"]:
                            if phrase.lower() in event.deal.item.name.lower() or event.deal.item.name.lower() == phrase.lower():
                                self.send_message(this_chat.id, "\n".join(auto_delivery["message"]))
                                break

                if self.config["playerok"]["bot"]["auto_complete_deals_enabled"]:
                    if event.deal.user.id != self.playerok_account.id:
                        self.playerok_account.update_deal(event.deal.id, ItemDealStatuses.SENT)
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новой сделки произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def handler_item_paid(plbot: PlayerokBot, event: ItemPaidEvent):
            try:
                if self.config["playerok"]["bot"]["auto_restore_items_enabled"]:
                    await self.restore_last_sold_item(event.deal.item)
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def handler_new_problem(plbot: PlayerokBot, event: ItemPaidEvent):
            try:
                self.logger.info(f"{PREFIX} {ACCENT_COLOR}🤬  Новая жалоба: {Fore.LIGHTWHITE_EX}{event.deal.user.username}{Fore.WHITE} открыл жалобу в сделке на покупку {Fore.LIGHTWHITE_EX}«{event.deal.item.name}»{Fore.WHITE}")
                if self.config["playerok"]["bot"]["tg_logging_enabled"] and self.config["playerok"]["bot"]["tg_logging_events"]["new_problem"]:
                    self.log_to_tg(log_text(f'🤬 Новая жалоба в <a href="https://playerok.com/deal/{event.deal.id}">сделке</a>', f"<b>Покупатель:</b> {event.deal.user.username}\n<b>Предмет:</b> {event.deal.item.name}\n"))
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента новых сообщений произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()

        async def handler_deal_status_changed(plbot: PlayerokBot, event: DealStatusChangedEvent):
            try:
                this_chat = event.chat
                if event.deal.status is ItemDealStatuses.PENDING: status = "В ожидании"
                elif event.deal.status is ItemDealStatuses.SENT: status = "Товар отправлен"
                elif event.deal.status is ItemDealStatuses.CONFIRMED: status = "Подтверждён"
                elif event.deal.status is ItemDealStatuses.ROLLED_BACK: status = "Возврат"
                self.logger.info(f"{PREFIX} {ACCENT_COLOR}🔄️📋  Статус сделки {Fore.LIGHTWHITE_EX}{event.deal.id}{ACCENT_COLOR} от {Fore.LIGHTWHITE_EX}{event.deal.user.username}{ACCENT_COLOR} изменился на {Fore.LIGHTWHITE_EX}«{status}»")
                if self.config["playerok"]["bot"]["tg_logging_enabled"] and self.config["playerok"]["bot"]["tg_logging_events"]["deal_status_changed"]:
                    self.log_to_tg(log_text(f'🔄️📋 Статус <a href="https://playerok.com/deal/{event.deal.id}/">сделки</a> изменился', f"<b>Новый статус:</b> {status}"))
                try:
                    if event.deal.status is ItemDealStatuses.CONFIRMED:
                        self.stats.orders_completed += 1
                        self.stats.earned_money += round(event.deal.transaction.value or 0, 2)
                    elif event.deal.status is ItemDealStatuses.ROLLED_BACK:
                        self.stats.orders_refunded += 1
                except Exception as e:
                    self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При подсчёте статистики произошла ошибка: {Fore.WHITE}{e}")
                finally:
                    set_stats(self.stats)

                if event.deal.status is ItemDealStatuses.CONFIRMED:
                    self.send_message(this_chat.id, self.msg("deal_confirmed"))
            except Exception:
                self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}При обработке ивента смены статуса сделки произошла ошибка: {Fore.WHITE}")
                traceback.print_exc()
            
        playerok_event_handlers = HandlersManager.get_playerok_event_handlers()
        playerok_event_handlers[EventTypes.NEW_MESSAGE].insert(0, handler_new_message)
        playerok_event_handlers[EventTypes.NEW_DEAL].insert(0, handler_new_deal)
        playerok_event_handlers[EventTypes.DEAL_STATUS_CHANGED].insert(0, handler_deal_status_changed)
        playerok_event_handlers[EventTypes.DEAL_HAS_PROBLEM].insert(0, handler_new_problem)
        playerok_event_handlers[EventTypes.ITEM_PAID].insert(0, handler_item_paid)
        HandlersManager.set_playerok_event_handlers(playerok_event_handlers)

        bot_event_handlers = HandlersManager.get_bot_event_handlers()
        def handle_on_playerok_bot_init():
            """ 
            Запускается при инициализации Playerok бота.
            Запускает за собой все хендлеры ON_PLAYEROK_BOT_INIT 
            """
            if "ON_PLAYEROK_BOT_INIT" in bot_event_handlers:
                for handler in bot_event_handlers["ON_PLAYEROK_BOT_INIT"]:
                    try:
                        handler(self)
                    except Exception as e:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Ошибка при обработке хендлера ивента ON_PLAYEROK_BOT_INIT: {Fore.WHITE}{e}")
        handle_on_playerok_bot_init()

        self.logger.info(f"{PREFIX} Слушатель событий запущен")
        listener = EventListener(self.playerok_account)
        for event in listener.listen(requests_delay=self.config["playerok"]["api"]["listener_requests_delay"]):
            playerok_event_handlers = HandlersManager.get_playerok_event_handlers() # чтобы каждый раз брать свежие хендлеры, ибо модули могут отключаться/включаться
            if event.type in playerok_event_handlers:
                for handler in playerok_event_handlers[event.type]:
                    try:
                        await handler(self, event)
                    except Exception as e:
                        self.logger.error(f"{PREFIX} {Fore.LIGHTRED_EX}Ошибка при обработке хендлера {handler} в ивенте {event.type.name}: {Fore.WHITE}{e}")